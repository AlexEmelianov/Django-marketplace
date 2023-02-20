from django.db import transaction
from services.data_access_objects import ProfileDAO
import logging

logger = logging.getLogger(__name__)


class ReplenishmentService:
    """ Сервис пополнения баланса пользователя """

    @classmethod
    def execute(cls, user_id: int, amount: int) -> None:
        profile = ProfileDAO.fetch_one(user_id=user_id)
        with transaction.atomic():
            profile.balance += amount
            ProfileDAO.update(profile=profile, update_fields=['balance'])
            logger.info(f'Balanse replenishment of the user {profile.username!r}, {amount=}')
