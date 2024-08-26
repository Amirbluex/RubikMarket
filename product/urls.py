from django.urls import path
from . import views

app_name = "product"

urlpatterns = [
    path('detail/<int:pk>', views.ProductDetailView.as_view(), name="product_detail"),
    path('list', views.ProductListView.as_view(), name="product_list"),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    ]
