from django.urls import path
from .views import login_view, register_view, logout_view, account_view, replenish_view, cart_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('account/', account_view, name='account'),
    path('account/replenish/', replenish_view, name='replenish'),
    path('cart/', cart_view, name='cart'),
]
