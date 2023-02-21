from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class AppUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_users'

    def ready(self):
        from app_shops import signals
        from .models import OrdersHistory

        model = OrdersHistory
        post_save.connect(signals.cache_delete, sender=model, dispatch_uid=f'{model}_post_save')
        post_delete.connect(signals.cache_delete, sender=model, dispatch_uid=f'{model}_post_delete')
