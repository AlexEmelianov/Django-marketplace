from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class AppUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_users'

    def ready(self):
        from . import signals
        from .models import OrdersHistory
        from django.contrib.sessions.models import Session

        model = OrdersHistory
        post_save.connect(signals.orders_cache_delete, sender=model, dispatch_uid=f'{model}_post_save')
        post_delete.connect(signals.orders_cache_delete, sender=model, dispatch_uid=f'{model}_post_delete')

        model = Session
        post_delete.connect(signals.cart_delete, sender=model, dispatch_uid=f'{model}_post_delete')
