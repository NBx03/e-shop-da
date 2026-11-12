import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id: int | str, text: str, parse_mode: str = "HTML", reply_markup: dict = None) -> bool:
    """
    Sends message via Telegram Bot API using HTTP POST.
    Safe and synchronous for Django signals/views.
    """
    token = getattr(settings, 'BOT_TOKEN', '')
    if not token or not chat_id:
        logger.warning(f"Telegram notification skipped: token or chat_id is missing. chat_id={chat_id}")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Telegram API error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.exception(f"Failed to send telegram message to {chat_id}: {e}")
        return False


def notify_admin_new_order(order):
    """
    Отправляет уведомление в чат магазина о новом заказе
    """
    admin_chat = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
    if not admin_chat:
        return

    items_text = "\n".join([
        f"• {item.product_title} — {item.quantity} шт. x {item.price} руб."
        for item in order.items.all()
    ])

    text = (
        f"🛒 <b>Новый заказ #{order.order_number}!</b>\n\n"
        f"👤 <b>Покупатель:</b> {order.customer_name}\n"
        f"📞 <b>Телефон:</b> {order.customer_phone}\n"
        f"🚚 <b>Доставка:</b> {order.get_delivery_method_display()}\n"
        f"📍 <b>Адрес:</b> {order.delivery_address or '—'}\n"
        f"💳 <b>Оплата:</b> {order.get_payment_method_display()} ({order.get_payment_status_display()})\n"
        f"💬 <b>Комментарий:</b> {order.comment or '—'}\n\n"
        f"📦 <b>Состав:</b>\n{items_text}\n\n"
        f"💰 <b>ИТОГО: {order.total_amount} руб.</b>"
    )
    send_telegram_message(admin_chat, text)


def notify_admin_payment_received(order):
    """
    Уведомление админа об успешной оплате онлайн
    """
    admin_chat = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
    if not admin_chat:
        return

    text = (
        f"💳 <b>Оплата получена!</b>\n\n"
        f"Заказ #{order.order_number}\n"
        f"Сумма: <b>{order.total_amount} руб.</b>\n"
        f"Покупатель: {order.customer_name} ({order.customer_phone})"
    )
    send_telegram_message(admin_chat, text)


def notify_admin_preorder(preorder):
    """
    Уведомление админа о заявке «Хочу такой»
    """
    admin_chat = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
    if not admin_chat:
        return

    text = (
        f"🔥 <b>Новая заявка «Хочу такой»!</b>\n\n"
        f"📱 <b>Товар:</b> {preorder.product.title}\n"
        f"💰 <b>Цена:</b> {preorder.product.price} руб.\n"
        f"👤 <b>Покупатель:</b> {preorder.customer_name}\n"
        f"📞 <b>Телефон:</b> {preorder.customer_phone}\n"
        f"📊 Всего заявок по товару: <b>{preorder.product.preorders_count}</b>"
    )
    send_telegram_message(admin_chat, text)


def notify_customer_order_status(order):
    """
    Уведомление покупателя об изменении статуса его заказа
    """
    if not order.telegram_user_id:
        return

    text = (
        f"📦 <b>Обновление по вашему заказу #{order.order_number}</b>\n\n"
        f"Текущий статус: <b>{order.get_status_display()}</b>\n"
        f"Статус оплаты: {order.get_payment_status_display()}\n\n"
        f"Благодарим за покупку в нашем магазине!"
    )
    send_telegram_message(order.telegram_user_id, text)


def notify_customer_tracking_number(order):
    """
    Отправляет покупателю трек-номер, когда менеджер внес его в админке
    """
    if not order.telegram_user_id or not order.tracking_number:
        return

    text = (
        f"🚚 <b>Ваш заказ #{order.order_number} передан в доставку!</b>\n\n"
        f"Ваш трек-номер для отслеживания:\n"
        f"👉 <code>{order.tracking_number}</code>\n\n"
        f"Способ доставки: {order.get_delivery_method_display()}\n"
        f"Вы можете отслеживать посылку на сайте перевозчика."
    )
    send_telegram_message(order.telegram_user_id, text)
