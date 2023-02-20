from django.urls import path
from .views import products_view, report_view

urlpatterns = [
    path('', products_view, name='products_list'),
    path('report/', report_view, name='report'),
]
