from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem
from apps.telegram_bot.services import notify_customer_tracking_number

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_title', 'price', 'quantity', 'item_subtotal')
    fields = ('product_title', 'price', 'quantity', 'item_subtotal')
    can_delete = False

    def item_subtotal(self, obj):
        return f"{obj.subtotal} руб."
    item_subtotal.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number_badge',
        'customer_name',
        'customer_phone',
        'delivery_method',
        'status',
        'payment_status_badge',
        'total_amount_display',
        'tracking_number_display',
        'created_at'
    )
    list_display_links = ('order_number_badge', 'customer_name')
    list_filter = ('status', 'payment_status', 'delivery_method', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_phone', 'tracking_number', 'delivery_address')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('id', 'order_number', 'total_amount', 'created_at', 'updated_at')
    save_on_top = True

    fieldsets = (
        ('Статус и трекинг', {
            'fields': ('status', 'tracking_number', 'payment_status')
        }),
        ('Клиент', {
            'fields': ('customer_name', 'customer_phone', 'telegram_user_id')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'delivery_address', 'comment')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'total_amount')
        }),
        ('Системные данные', {
            'classes': ('collapse',),
            'fields': ('id', 'order_number', 'created_at', 'updated_at')
        }),
    )

    def order_number_badge(self, obj):
        return format_html('<b>#{}</b>', obj.order_number)
    order_number_badge.short_description = "№ Заказа"

    def status_badge(self, obj):
        colors = {
            'new': '#3B82F6',        # Blue
            'paid': '#10B981',       # Emerald
            'packing': '#F59E0B',    # Amber
            'shipped': '#8B5CF6',    # Purple
            'delivered': '#059669',  # Green
            'cancelled': '#EF4444',  # Red
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Статус заказа"

    def payment_status_badge(self, obj):
        colors = {
            'pending': '#F59E0B',
            'paid': '#10B981',
            'failed': '#EF4444'
        }
        color = colors.get(obj.payment_status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 11px;">● {}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = "Оплата"

    def total_amount_display(self, obj):
        return format_html('<b>{} ₽</b>', obj.total_amount)
    total_amount_display.short_description = "Сумма"

    def tracking_number_display(self, obj):
        if obj.tracking_number:
            return format_html('<code>{}</code>', obj.tracking_number)
        return format_html('<span style="color: #9CA3AF;">—</span>')
    tracking_number_display.short_description = "Трек"

    actions = ['resend_tracking_telegram', 'mark_as_shipped']

    @admin.action(description="Повторно отправить трек-номер покупателю в Telegram")
    def resend_tracking_telegram(self, request, queryset):
        count = 0
        for order in queryset:
            if order.tracking_number and order.telegram_user_id:
                notify_customer_tracking_number(order)
                count += 1
        self.message_user(request, f"Уведомление с трек-номером отправлено для {count} заказов.")

    @admin.action(description="Перевести в статус «Отправлен»")
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"{updated} заказов переведены в статус «Отправлен».")
