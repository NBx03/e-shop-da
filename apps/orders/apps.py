from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Заказы и оплата'

    def ready(self):
        import apps.orders.signals  # noqa
