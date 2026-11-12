import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product, ProductStatus
from apps.orders.models import Order, OrderItem, DeliveryMethod, PaymentMethod, OrderStatus, PaymentStatus

class OrderCreationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Телефоны", slug="phones")
        self.product1 = Product.objects.create(
            category=self.category,
            title="iPhone 15",
            slug="iphone-15",
            price=Decimal('100000.00'),
            status=ProductStatus.IN_STOCK
        )
        self.product2 = Product.objects.create(
            category=self.category,
            title="Чехол",
            slug="case",
            price=Decimal('2000.00'),
            status=ProductStatus.IN_STOCK
        )

    def test_create_order_success(self):
        payload = {
            'customer_name': 'Иван Иванов',
            'customer_phone': '+79991234567',
            'delivery_method': DeliveryMethod.PICKUP,
            'payment_method': PaymentMethod.CASH_ON_DELIVERY,
            'items': [
                {'id': self.product1.id, 'quantity': 1},
                {'id': self.product2.id, 'quantity': 2},
            ]
        }
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_amount'], 104000.00)

        # Verify DB records
        order = Order.objects.get(id=data['order_id'])
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_amount, Decimal('104000.00'))

    def test_postal_delivery_with_cod_rejected(self):
        # COD is not allowed for postal delivery
        payload = {
            'customer_name': 'Иван Иванов',
            'customer_phone': '+79991234567',
            'delivery_method': DeliveryMethod.POSTAL,
            'delivery_address': 'г. Казань, ул. Ленина, 5',
            'payment_method': PaymentMethod.CASH_ON_DELIVERY,
            'items': [{'id': self.product1.id, 'quantity': 1}]
        }
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("только онлайн-оплата", data['error'])

    def test_tampered_initdata_rejected_with_403(self):
        payload = {
            'customer_name': 'Хакер',
            'customer_phone': '+79990000000',
            'delivery_method': DeliveryMethod.PICKUP,
            'payment_method': PaymentMethod.ONLINE,
            'items': [{'id': self.product1.id, 'quantity': 1}],
            'initData': 'query_id=fake&user={"id":123}&hash=tampered_bad_hash'
        }
        response = self.client.post(
            reverse('api_create_order'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
