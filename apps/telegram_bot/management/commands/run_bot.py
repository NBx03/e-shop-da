import asyncio
from django.core.management.base import BaseCommand
from apps.telegram_bot.bot import main

class Command(BaseCommand):
    help = "Запускает Telegram бота (Long Polling)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск Telegram бота..."))
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Бот остановлен пользователем."))
