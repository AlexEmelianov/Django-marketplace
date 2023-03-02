from django.core.cache import cache
from app_users.models import Cart


def orders_cache_delete(sender, instance=None, **kwargs):
    """ Clears cache of OrdersHistory model. """

    cache.delete(f'orders_{instance.user.get_username()}')


def cart_delete(sender, instance, **kwargs):
    """ Deletes expired cart of anonymous user. """

    Cart.objects.filter(cart_id=instance.session_key).delete()
