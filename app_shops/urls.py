from django.urls import path
from .views import products_list_view, report_view

urlpatterns = [
    path('', products_list_view, name='products_list'),
    path('report/', report_view, name='report'),
]
