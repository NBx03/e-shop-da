from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('terms/', views.terms_view, name='terms'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<str:slug_or_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/preorder/', views.api_preorder, name='api_preorder'),
]
