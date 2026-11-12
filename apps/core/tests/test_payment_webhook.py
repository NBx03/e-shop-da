import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.orders.models import Order, OrderStatus, PaymentStatus

class PaymentWebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = Order.objects.create(
            customer_name="Тестовый Покупатель",
            customer_phone="+79998887766",
            total_amount=Decimal('50000.00'),
            payment_status=PaymentStatus.PENDING,
            status=OrderStatus.NEW
        )

    def test_payment_webhook_success(self):
        payload = {
            'order_id': str(self.order.id),
            'status': 'success'
        }
        response = self.client.post(
            reverse('api_payment_webhook'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, PaymentStatus.PAID)
        self.assertEqual(self.order.status, OrderStatus.PAID)

    def test_payment_webhook_failed(self):
        payload = {
            'order_id': str(self.order.id),
            'status': 'failed'
        }
        response = self.client.post(
            reverse('api_payment_webhook'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, PaymentStatus.FAILED)
        self.assertEqual(self.order.status, OrderStatus.NEW)
