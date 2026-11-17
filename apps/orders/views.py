import json
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Order, OrderItem, DeliveryMethod, PaymentMethod, OrderStatus, PaymentStatus
from apps.catalog.models import Product
from apps.core.telegram_auth import verify_telegram_init_data
from apps.core.validators import validate_and_clean_phone
from apps.telegram_bot.services import (
    notify_admin_new_order,
    notify_admin_payment_received,
    notify_customer_order_status
)

@csrf_exempt
def api_create_order(request):
    """
    Создание заказа.
    Проверяет:
    1. initData Telegram (если передано) - поддельные данные отклоняются с 403
    2. Правило доставки и оплаты (наложенный платеж только для самовывоза и курьера)
    3. Подсчет итоговой суммы по актуальным ценам БД
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST method allowed")

    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    customer_name = body.get('customer_name', '').strip()
    customer_phone = body.get('customer_phone', '').strip()
    delivery_method = body.get('delivery_method', DeliveryMethod.PICKUP)
    delivery_address = body.get('delivery_address', '').strip()
    comment = body.get('comment', '').strip()
    payment_method = body.get('payment_method', PaymentMethod.ONLINE)
    items_data = body.get('items', [])
    init_data_raw = body.get('initData', '')

    if not customer_name or not customer_phone:
        return JsonResponse({'error': 'Укажите имя и контактный телефон'}, status=400)

    # Валидация и нормализация номера телефона
    is_phone_valid, normalized_phone, phone_err = validate_and_clean_phone(customer_phone)
    if not is_phone_valid:
        return JsonResponse({'error': phone_err}, status=400)
    customer_phone = normalized_phone

    if not items_data or not isinstance(items_data, list):
        return JsonResponse({'error': 'Корзина пуста'}, status=400)

    # Валидация правил доставки и оплаты
    if delivery_method == DeliveryMethod.POSTAL and payment_method == PaymentMethod.CASH_ON_DELIVERY:
        return JsonResponse({
            'error': 'При отправке в регионы доступна только онлайн-оплата'
        }, status=400)

    if delivery_method in (DeliveryMethod.COURIER, DeliveryMethod.POSTAL) and not delivery_address:
        return JsonResponse({'error': 'Для доставки необходимо указать адрес'}, status=400)

    # Проверка Telegram initData
    telegram_user_id = None
    if init_data_raw:
        is_valid, parsed_data, err_msg = verify_telegram_init_data(init_data_raw)
        if not is_valid:
            # Требование ТЗ: запрос с поддельными данными получает отказ
            return JsonResponse({'error': f'Ошибка авторизации Telegram: {err_msg}'}, status=403)
        if parsed_data and 'user' in parsed_data:
            telegram_user_id = parsed_data['user'].get('id')

    # Расчет суммы и сбор товаров
    order_items_to_create = []
    total_amount = Decimal('0.00')

    for itm in items_data:
        prod_id = itm.get('id')
        qty = int(itm.get('quantity', 1))
        if qty <= 0:
            continue
        try:
            prod = Product.objects.get(id=prod_id, is_active=True)
        except Product.DoesNotExist:
            return JsonResponse({'error': f'Товар с ID {prod_id} не найден или скрыт'}, status=400)

        item_subtotal = prod.price * qty
        total_amount += item_subtotal
        order_items_to_create.append({
            'product': prod,
            'title': prod.title,
            'price': prod.price,
            'quantity': qty
        })

    if not order_items_to_create:
        return JsonResponse({'error': 'Корзина не содержит доступных товаров'}, status=400)

    # Защита от дабл-клика / идемпотентность: проверяем не был ли отправлен дубликат за последние 10 секунд
    recent_duplicate = Order.objects.filter(
        customer_phone=customer_phone,
        total_amount=total_amount,
        created_at__gte=timezone.now() - timedelta(seconds=10)
    ).order_by('-created_at').first()

    if recent_duplicate:
        payment_url = f"/orders/payment/mock/{recent_duplicate.id}/" if recent_duplicate.payment_method == PaymentMethod.ONLINE else None
        return JsonResponse({
            'success': True,
            'order_id': str(recent_duplicate.id),
            'order_number': recent_duplicate.order_number,
            'payment_url': payment_url,
            'total_amount': float(recent_duplicate.total_amount),
            'message': 'Заказ уже оформлен'
        })

    # Создание заказа в базе данных (атомарная транзакция)
    with transaction.atomic():
        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            telegram_user_id=telegram_user_id,
            delivery_method=delivery_method,
            delivery_address=delivery_address,
            comment=comment,
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING,
            status=OrderStatus.NEW,
            total_amount=total_amount
        )

        for itm in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                product=itm['product'],
                product_title=itm['title'],
                price=itm['price'],
                quantity=itm['quantity']
            )

    # Уведомление магазина
    notify_admin_new_order(order)

    payment_url = None
    if payment_method == PaymentMethod.ONLINE:
        payment_url = f"/orders/payment/mock/{order.id}/"

    return JsonResponse({
        'success': True,
        'order_id': str(order.id),
        'order_number': order.order_number,
        'payment_url': payment_url,
        'total_amount': float(order.total_amount),
        'message': 'Заказ успешно создан'
    })


def payment_mock_view(request, order_id):
    """
    Отдельная страница «оплата» - заглушка платежного шлюза банка.
    Содержит информацию о заказе и кнопки: «Оплата прошла» и «Отказ».
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment_mock.html', {'order': order})


@csrf_exempt
def api_payment_webhook(request):
    """
    Эндпоинт вебхука от платежного сервиса.
    Принимает POST с order_id и статусом платежа.
    Меняет статус заказа и шлет уведомления.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    order_id = data.get('order_id')
    event_status = data.get('status')  # 'success' or 'failed'

    if not order_id or not event_status:
        return JsonResponse({'error': 'Missing order_id or status'}, status=400)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if event_status == 'success':
        order.payment_status = PaymentStatus.PAID
        order.status = OrderStatus.PAID
        order.save(update_fields=['payment_status', 'status'])
        
        # Уведомления
        notify_admin_payment_received(order)
        notify_customer_order_status(order)
        return JsonResponse({'status': 'ok', 'order_status': order.status, 'message': 'Payment confirmed'})
    else:
        order.payment_status = PaymentStatus.FAILED
        order.save(update_fields=['payment_status'])
        return JsonResponse({'status': 'ok', 'order_status': order.status, 'message': 'Payment cancelled/failed'})


def order_status_view(request, order_id):
    """
    Страница успешного завершения или статуса заказа
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_status.html', {'order': order})
