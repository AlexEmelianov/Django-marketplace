from django.core.cache import cache
from app_users.models import Cart


def orders_cache_delete(sender, instance=None, **kwargs):
    """ Сбрасывает кэш при изменении истории заказов (OrdersHistory) """

    cache.delete(f'orders_{instance.user.get_username()}')


def cart_delete(sender, instance=None, **kwargs):
    """ Удаляет корзину анонимного пользователя после истечения сессии """

    Cart.objects.filter(cart_id=instance.session_key).delete()
