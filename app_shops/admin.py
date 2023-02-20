from django.contrib import admin
from .models import Product, Shop


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name if field.name != 'description' else 'description_100char' for field in Product._meta.fields]


class ProductInline(admin.TabularInline):
    model = Product


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = [field.name if field.name != 'description' else 'description_100char' for field in Shop._meta.fields]
    inlines = ProductInline,
