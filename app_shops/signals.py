from django.core.cache import cache

PRODUCTS_KEY = 'products'


def products_cache_delete(sender, instance=None, **kwargs):
    """ Clears cache of Product и Shop models. """

    cache.delete(PRODUCTS_KEY)
