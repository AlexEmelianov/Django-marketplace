from django.core.cache import cache

PRODUCTS_KEY = 'products'


def products_cache_delete(sender, instance=None, **kwargs):
    """ Сбрасывает кэш при изменении товаров и магазинов (Product и Shop) """

    cache.delete(PRODUCTS_KEY)
