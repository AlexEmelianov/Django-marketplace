from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, OrdersHistory
from django.utils.translation import gettext_lazy as _


class OrderLineInline(admin.TabularInline):
    model = OrdersHistory.order_lines.through


@admin.register(OrdersHistory)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrdersHistory._meta.fields]
    inlines = OrderLineInline,


# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Profile._meta.fields]
class ProfileInline(admin.TabularInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('profiles')


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
