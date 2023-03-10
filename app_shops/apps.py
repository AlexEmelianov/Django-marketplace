from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class AppShopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_shops'

    def ready(self):
        """ Binds django signals with handlers. """

        from . import signals
        from .models import Product, Shop

        for model in Product, Shop:
            post_save.connect(signals.products_cache_delete, sender=model, dispatch_uid=f'{model}_post_save')
            post_delete.connect(signals.products_cache_delete, sender=model, dispatch_uid=f'{model}_post_delete')
