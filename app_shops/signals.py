from django.core.cache import cache
from app_users.models import OrdersHistory
from .models import Product, Shop
import logging

logger = logging.getLogger(__name__)
PRODUCTS_SHOPS_KEY = 'products_shops'


def cache_delete(sender, instance=None, **kwargs):
    """ Сбрасывает кэш при изменении моделей """

    logger.debug(f'Receiving signal from {sender!r} with {instance=!r}')
    if sender in (Product, Shop):
        cache.delete(PRODUCTS_SHOPS_KEY)
    elif sender == OrdersHistory:
        cache.delete(f'orders_{instance.user.username}')
