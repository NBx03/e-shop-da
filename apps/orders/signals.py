from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order
from apps.telegram_bot.services import (
    notify_customer_tracking_number,
    notify_customer_order_status,
)

@receiver(pre_save, sender=Order)
def check_order_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_tracking = old_instance.tracking_number
        except Order.DoesNotExist:
            instance._old_status = None
            instance._old_tracking = None
    else:
        instance._old_status = None
        instance._old_tracking = None


@receiver(post_save, sender=Order)
def handle_order_notifications(sender, instance, created, **kwargs):
    if created:
        return

    # Check if tracking number is new or changed
    if instance.tracking_number and instance.tracking_number != getattr(instance, '_old_tracking', None):
        if instance.tracking_number != instance.last_notified_tracking:
            notify_customer_tracking_number(instance)
            # Update last_notified_tracking without triggering endless signals
            Order.objects.filter(pk=instance.pk).update(last_notified_tracking=instance.tracking_number)

    # Check if order status changed
    old_status = getattr(instance, '_old_status', None)
    if old_status and old_status != instance.status:
        notify_customer_order_status(instance)
