from django.utils.translation import gettext as _
from django.db import transaction
from services.data_access_objects import CartDAO, ProfileDAO, OrderDAO, ProductDAO
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """ Сервис оформления заказа """

    @classmethod
    def execute(cls, user_id: int) -> str:
        cart = CartDAO.fetch(cart_id=f'{user_id}', threshold_quantity=1)
        if not cart:
            return _('Put something in the cart first!')
        cart_sum = sum(cart_line.line_total for cart_line in cart)  # Сумма корзины
        profile = ProfileDAO.fetch_one(user_id=user_id)
        if profile.balance < cart_sum:
            return _('Insufficient funds')
        with transaction.atomic():
            profile.balance -= cart_sum  # Уменьшаем баланс
            ProductDAO.minus_remains(cart=cart)  # Уменьшаем остаток товара на складе
            OrderDAO.create(user_id=user_id, total=cart_sum, cart=cart)  # Создаем историю заказа
            CartDAO.delete(cart_id=f'{user_id}')  # Удаляем корзину
            total = OrderDAO.get_total(user_id=user_id)  # Получаем сумму  всех заказов
            prev_status = profile.status
            if total < 1e3:             # Проверяем сумму заказов и меняем статус
                profile.status = profile.status_choices[0][1]
            elif 1e3 <= total < 1e4:
                profile.status = profile.status_choices[1][1]
            elif total >= 1e4:
                profile.status = profile.status_choices[2][1]
            ProfileDAO.update(profile=profile, update_fields=['balance', 'status'])
            logger.info(f'Placing an order by user {profile.username!r} in the amount of {cart_sum} rub.')
            message = _('Payment successful') + '.\n'
            if prev_status != profile.status:
                logger.info(f'Status changing of the user {profile.username!r} ({prev_status} --> {profile.status})')
                message += _(f'Congratulations! Your status has been changed') + f': {prev_status} -> {profile.status})'
        return message
