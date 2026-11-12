from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product, ProductImage, PreorderRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'products_count')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "Товаров"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Превью"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'category',
        'price',
        'status_badge',
        'preorders_badge',
        'is_active',
        'created_at'
    )
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('status', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'slug')
    list_editable = ('price', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    save_on_top = True

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'category', 'is_active')
        }),
        ('Цены и статус', {
            'fields': ('price', 'old_price', 'status')
        }),
        ('Изображение', {
            'fields': ('main_image', 'image_preview')
        }),
        ('Описание и характеристики', {
            'fields': ('description', 'characteristics')
        }),
        ('Системная информация', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )

    def image_thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px;" />', obj.main_image.url)
        return format_html('<span style="color:#aaa;">Без фото</span>')
    image_thumbnail.short_description = "Фото"

    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-width: 200px; border-radius: 8px;" />', obj.main_image.url)
        return "Изображение еще не загружено"
    image_preview.short_description = "Текущее фото (WebP)"

    def status_badge(self, obj):
        colors = {
            'in_stock': '#10B981',  # green
            'on_the_way': '#F59E0B', # orange
            'preorder': '#6366F1'    # indigo
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Статус"

    def preorders_badge(self, obj):
        count = obj.preorders_count
        if count > 0:
            url = reverse('admin:catalog_preorderrequest_changelist') + f'?product__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="background-color: #EF4444; color: white; padding: 2px 7px; border-radius: 9999px; font-size: 11px; text-decoration: none; font-weight: 600;">🔥 {} заявок</a>',
                url,
                count
            )
        return format_html('<span style="color: #9CA3AF; font-size: 11px;">0</span>')
    preorders_badge.short_description = "Заявки «Хочу такой»"


@admin.register(PreorderRequest)
class PreorderRequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer_name', 'customer_phone', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at', 'product__category')
    search_fields = ('customer_name', 'customer_phone', 'product__title')
    list_editable = ('is_processed',)
    readonly_fields = ('created_at',)
