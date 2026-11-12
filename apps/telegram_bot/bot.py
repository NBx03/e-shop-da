import asyncio
import logging
import os
import django

# Initialize Django standalone if run directly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp
from apps.orders.models import Order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
dp = Dispatcher()

def get_shop_keyboard(startapp_param: str = None) -> InlineKeyboardMarkup:
    base_url = settings.WEBAPP_URL.rstrip('/')
    target_url = f"{base_url}/?tgWebAppStartParam={startapp_param}" if startapp_param else base_url
    
    button_text = "🛍️ Открыть товар в магазине" if startapp_param else "🛍️ Открыть магазин электроники"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, web_app=WebAppInfo(url=target_url))]
    ])


@dp.message(CommandStart())
async def handle_start(message: types.Message, command: CommandObject):
    start_param = command.args  # e.g. /start iphone_15_pro
    bot_info = await message.bot.get_me()

    if start_param:
        text = (
            f"👋 <b>Здравствуйте, {message.from_user.first_name}!</b>\n\n"
            f"Вы перешли по ссылке на товар. Нажмите кнопку ниже, чтобы открыть карточку товара в Mini App:"
        )
        await message.answer(text, reply_markup=get_shop_keyboard(start_param), parse_mode="HTML")
    else:
        text = (
            f"👋 <b>Добро пожаловать в интернет-магазин электроники!</b>\n\n"
            f"У нас вы найдете смартфоны, ноутбуки, гаджеты и аксессуары по выгодным ценам.\n\n"
            f"• Доставка по городу, самовывоз и отправка в регионы\n"
            f"• Гарантия качества на всю технику\n"
            f"• Уведомления о статусе заказа и трек-номере прямо сюда\n\n"
            f"Нажмите <b>«Открыть магазин»</b>, чтобы перейти к каталогу."
        )
        await message.answer(text, reply_markup=get_shop_keyboard(), parse_mode="HTML")


@dp.message(Command("orders"))
async def handle_my_orders(message: types.Message):
    """
    Показывает историю заказов пользователя по его telegram_user_id
    """
    user_id = message.from_user.id
    orders = Order.objects.filter(telegram_user_id=user_id).order_by('-created_at')[:5]

    if not orders.exists():
        await message.answer("У вас пока нет оформленных заказов через Telegram.")
        return

    text_lines = ["📋 <b>Ваши последние заказы:</b>\n"]
    for ord in orders:
        track_info = f"\n   🚚 Трек-номер: <code>{ord.tracking_number}</code>" if ord.tracking_number else ""
        text_lines.append(
            f"• <b>Заказ #{ord.order_number}</b> — {ord.total_amount} ₽\n"
            f"   Статус: {ord.get_status_display()} ({ord.get_payment_status_display()}){track_info}\n"
        )

    await message.answer("\n".join(text_lines), parse_mode="HTML")


@dp.message(Command("share"))
async def handle_share(message: types.Message, command: CommandObject):
    """
    Генерирует ссылку для поста в канале со startapp-параметром
    """
    bot_info = await message.bot.get_me()
    slug = command.args or "iphone-15-pro-max"
    link = f"https://t.me/{bot_info.username}?startapp={slug}"
    text = (
        f"🔗 <b>Прямая ссылка на товар для постов:</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"При клике на эту ссылку у подписчика сразу откроется карточка товара в Mini App!"
    )
    await message.answer(text, parse_mode="HTML")


async def main():
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN is not configured in settings/.env!")
        return
    logger.info("Starting Telegram Bot (long polling)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
