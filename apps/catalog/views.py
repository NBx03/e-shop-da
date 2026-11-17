import json
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Product, PreorderRequest
from apps.core.telegram_auth import verify_telegram_init_data
from apps.core.validators import validate_and_clean_phone
from apps.telegram_bot.services import notify_admin_preorder

def index_view(request):
    """
    Главная страница Mini App и браузерной версии.
    Один каталог, два входа:
    - Из бота по кнопке (и по ссылке startapp=slug)
    - В обычном браузере
    """
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    startapp = request.GET.get('tgWebAppStartParam') or request.GET.get('startapp') or ''
    
    context = {
        'categories': categories,
        'startapp_slug': startapp,
    }
    return render(request, 'index.html', context)


def terms_view(request):
    """
    Страница-заглушка пользовательского соглашения и оферты
    """
    return render(request, 'terms.html')


def api_products(request):
    """
    JSON API списка товаров с фильтрацией, поиском и сортировкой
    """
    category_id = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'popular')  # popular, price_asc, price_desc

    products = Product.objects.filter(is_active=True).select_related('category')

    if category_id and category_id != 'all':
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(title__icontains=search_query) | products.filter(description__icontains=search_query)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    data = []
    for p in products:
        data.append({
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'price': float(p.price),
            'old_price': float(p.old_price) if p.old_price else None,
            'category_id': p.category_id,
            'category_name': p.category.name,
            'status': p.status,
            'status_label': p.get_status_display(),
            'main_image': f"{p.main_image.url}?v=realphotos3" if p.main_image else '',
            'preorders_count': p.preorders_count,
        })

    return JsonResponse({'products': data})


def api_product_detail(request, slug_or_id):
    """
    JSON API детальной информации о товаре с галереей и характеристиками
    """
    if str(slug_or_id).isdigit():
        product = get_object_or_404(Product, id=int(slug_or_id), is_active=True)
    else:
        product = get_object_or_404(Product, slug=slug_or_id, is_active=True)

    gallery = [f"{img.image.url}?v=realphotos3" for img in product.gallery_images.all()]
    if product.main_image and f"{product.main_image.url}?v=realphotos3" not in gallery:
        gallery.insert(0, f"{product.main_image.url}?v=realphotos3")

    data = {
        'id': product.id,
        'title': product.title,
        'slug': product.slug,
        'price': float(product.price),
        'old_price': float(product.old_price) if product.old_price else None,
        'description': product.description,
        'characteristics': product.characteristics or {},
        'status': product.status,
        'status_label': product.get_status_display(),
        'gallery': gallery,
        'category_name': product.category.name,
        'preorders_count': product.preorders_count,
    }
    return JsonResponse(data)


@csrf_exempt
def api_preorder(request):
    """
    Создание заявки «Хочу такой» для товаров со статусом 'preorder'
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    product_id = body.get('product_id')
    customer_name = body.get('name', '').strip()
    customer_phone = body.get('phone', '').strip()
    init_data_raw = body.get('initData', '')

    if not product_id or not customer_name or not customer_phone:
        return JsonResponse({'error': 'Заполните имя и телефон'}, status=400)

    # Валидация и нормализация номера телефона
    is_phone_valid, normalized_phone, phone_err = validate_and_clean_phone(customer_phone)
    if not is_phone_valid:
        return JsonResponse({'error': phone_err}, status=400)
    customer_phone = normalized_phone

    product = get_object_or_404(Product, id=product_id)

    telegram_user_id = None
    if init_data_raw:
        is_valid, parsed_data, _ = verify_telegram_init_data(init_data_raw)
        if is_valid and parsed_data and 'user' in parsed_data:
            telegram_user_id = parsed_data['user'].get('id')

    # Защита от спама/дабл-клика: проверяем дубликат за последние 15 секунд
    recent_duplicate = PreorderRequest.objects.filter(
        product=product,
        customer_phone=customer_phone,
        created_at__gte=timezone.now() - timedelta(seconds=15)
    ).first()

    if recent_duplicate:
        return JsonResponse({
            'success': True,
            'preorders_count': product.preorders_count,
            'message': 'Заявка уже была принята ранее!'
        })

    with transaction.atomic():
        preorder = PreorderRequest.objects.create(
            product=product,
            customer_name=customer_name,
            customer_phone=customer_phone,
            telegram_user_id=telegram_user_id
        )

    # Уведомляем администратора магазина в Telegram
    notify_admin_preorder(preorder)

    return JsonResponse({
        'success': True,
        'preorders_count': product.preorders_count,
        'message': 'Заявка успешно принята! Мы сообщим вам, когда товар появится в наличии.'
    })
