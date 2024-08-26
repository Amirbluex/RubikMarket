from django.urls import path, include
from . import views

app_name = 'account'

address_patterns = [
    path('', views.AddressListCreationView.as_view(), name='add_list_address'),
    path('del/<int:pk>/', views.AddressDelete.as_view(), name='remove_address'),
    path('set-active/<int:pk>/', views.AddressSetActive.as_view(), name='set_active_address'),
]

urlpatterns = [
    path('login', views.UserLogin.as_view(), name='user_login'),
    path('logout', views.user_logout, name='user_logout'),
    path('register', views.UserRegister.as_view(), name='user_register'),
    path('my-account/', include(
            [
                path('', views.UserProfileView.as_view(), name='user_profile'),
                path('factors/', views.UserOrdersView.as_view(), name='factors'),
                path('address/', include(address_patterns)),
            ]
        )
    ),
    ]
