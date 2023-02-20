from django.contrib import admin
from .models import Profile, OrdersHistory


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]


class OrderLineInline(admin.TabularInline):
    model = OrdersHistory.order_lines.through


@admin.register(OrdersHistory)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrdersHistory._meta.fields]
    inlines = OrderLineInline,
