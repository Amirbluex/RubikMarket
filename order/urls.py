from django.urls import path

from . import views

app_name = 'order'

urlpatterns = [
    path('detail/', views.CartDetailView.as_view(), name='cart_detail'),
    path('add/<int:pk>/', views.CartAddView.as_view(), name='cart_add'),
    path('remove/<int:pk>/', views.CartItemRemoveView.as_view(), name='cart_item_remove'),
    path('delete/', views.CartDeleteView.as_view(), name='cart_delete'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/create/', views.OrderCreationView.as_view(), name='order_create'),
    path('order/pay/<int:pk>/', views.SendRequestView.as_view(), name='zarinpal_pay'),
    path('order/verify/', views.VerifyOrderView.as_view(), name='verify_order'),
]
