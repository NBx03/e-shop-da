import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.catalog.models import Product

class DeliveryMethod(models.TextChoices):
    PICKUP = 'pickup', 'Самовывоз'
    COURIER = 'courier', 'Доставка по городу'
    POSTAL = 'postal', 'Отправка в регионы'


class PaymentMethod(models.TextChoices):
    ONLINE = 'online', 'Онлайн-оплата'
    CASH_ON_DELIVERY = 'cod', 'При получении'


class OrderStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    PAID = 'paid', 'Оплачен'
    PACKING = 'packing', 'Собирается'
    SHIPPED = 'shipped', 'Отправлен'
    DELIVERED = 'delivered', 'Выдан'
    CANCELLED = 'cancelled', 'Отменен'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает оплаты'
    PAID = 'paid', 'Оплачено'
    FAILED = 'failed', 'Ошибка оплаты'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.PositiveIntegerField(unique=True, verbose_name="Номер заказа")
    
    # Customer
    customer_name = models.CharField(max_length=150, verbose_name="Имя покупателя")
    customer_phone = models.CharField(max_length=30, verbose_name="Телефон покупателя")
    telegram_user_id = models.BigIntegerField(null=True, blank=True, verbose_name="Telegram User ID")
    
    # Delivery
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.PICKUP,
        verbose_name="Способ получения"
    )
    delivery_address = models.TextField(blank=True, verbose_name="Адрес доставки")
    comment = models.TextField(blank=True, verbose_name="Комментарий к заказу")
    
    # Payment & Status
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.ONLINE,
        verbose_name="Способ оплаты"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="Статус оплаты"
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name="Статус заказа"
    )
    
    # Tracking
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Трек-номер посылки"
    )
    last_notified_tracking = models.CharField(
        max_length=100,
        blank=True,
        editable=False,
        verbose_name="Последний отправленный трек-номер"
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Итоговая сумма (руб.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def clean(self):
        # Validation rule: COD is only allowed for pickup and courier delivery
        if self.delivery_method == DeliveryMethod.POSTAL and self.payment_method == PaymentMethod.CASH_ON_DELIVERY:
            raise ValidationError("Для отправки в регионы доступна только онлайн-оплата.")

    def save(self, *args, **kwargs):
        if not self.order_number:
            last = Order.objects.order_by('-order_number').first()
            self.order_number = (last.order_number + 1) if last and last.order_number else 1001
        self.full_clean()
        super().save(*args, **kwargs)

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def __str__(self):
        return f"Заказ #{self.order_number} ({self.customer_name}) — {self.total_amount} руб. [{self.get_status_display()}]"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="Товар"
    )
    product_title = models.CharField(max_length=255, verbose_name="Название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за шт. (руб.)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_title} x {self.quantity} = {self.subtotal} руб."
