import os
from django.db import models
from django.utils.text import slugify
from apps.core.image_utils import convert_image_to_webp

class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")
    slug = models.SlugField(max_length=160, unique=True, blank=True, verbose_name="Слаг")
    icon = models.CharField(max_length=50, blank=True, default="grid", verbose_name="Иконка (lucide)")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Раздел каталога"
        verbose_name_plural = "Разделы каталога"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or f"category-{self.order}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductStatus(models.TextChoices):
    IN_STOCK = 'in_stock', 'В наличии'
    ON_THE_WAY = 'on_the_way', 'В пути'
    PREORDER = 'preorder', 'Под заказ'


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Раздел"
    )
    title = models.CharField(max_length=255, verbose_name="Название товара")
    slug = models.SlugField(max_length=260, unique=True, blank=True, verbose_name="Слаг / startapp ID")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (руб.)")
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена (руб.)"
    )
    description = models.TextField(verbose_name="Описание товара")
    characteristics = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Характеристики (JSON: { 'Цвет': 'Черный', ... })"
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.IN_STOCK,
        verbose_name="Статус товара"
    )
    main_image = models.ImageField(
        upload_to="products/main/",
        blank=True,
        null=True,
        verbose_name="Главное фото (WebP)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Отображать в каталоге")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True) or f"prod-{self.pk or 0}"
        
        # Convert main image to WebP if newly uploaded and not already webp
        if self.main_image and hasattr(self.main_image, 'file'):
            ext = os.path.splitext(self.main_image.name)[1].lower()
            if ext != '.webp':
                webp_file = convert_image_to_webp(self.main_image)
                if webp_file:
                    self.main_image.save(webp_file.name, webp_file, save=False)

        super().save(*args, **kwargs)

    @property
    def preorders_count(self):
        return self.preorder_requests.count()

    def __str__(self):
        return f"{self.title} ({self.get_status_display()}) - {self.price} руб."


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="Товар"
    )
    image = models.ImageField(
        upload_to="products/gallery/",
        verbose_name="Фото галереи (WebP)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Галерея фото"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            ext = os.path.splitext(self.image.name)[1].lower()
            if ext != '.webp':
                webp_file = convert_image_to_webp(self.image)
                if webp_file:
                    self.image.save(webp_file.name, webp_file, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Фото для {self.product.title}"


class PreorderRequest(models.Model):
    """
    Заявка «Хочу такой» для товаров под заказ
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="preorder_requests",
        verbose_name="Товар под заказ"
    )
    customer_name = models.CharField(max_length=150, verbose_name="Имя покупателя")
    customer_phone = models.CharField(max_length=30, verbose_name="Телефон")
    telegram_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Telegram User ID"
    )
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")
    comment = models.TextField(blank=True, verbose_name="Заметка менеджера")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")

    class Meta:
        verbose_name = "Заявка «Хочу такой»"
        verbose_name_plural = "Заявки «Хочу такой»"
        ordering = ['-created_at']

    def __str__(self):
        return f"Хочу такой: {self.product.title} от {self.customer_name} ({self.customer_phone})"
