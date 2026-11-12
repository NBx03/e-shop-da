from django.urls import path
from . import views

urlpatterns = [
    path('api/create/', views.api_create_order, name='api_create_order'),
    path('payment/mock/<uuid:order_id>/', views.payment_mock_view, name='payment_mock'),
    path('payment/webhook/', views.api_payment_webhook, name='api_payment_webhook'),
    path('status/<uuid:order_id>/', views.order_status_view, name='order_status'),
]
