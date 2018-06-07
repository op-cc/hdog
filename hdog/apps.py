from django.apps import AppConfig
from django.db.models.signals import m2m_changed


class HDogConfig(AppConfig):
    name = 'hdog'
    verbose_name = 'Складской учет'

    def ready(self):
        from .models import TransferedGoods
        from .signal_handlers import update_inv_numbers_on_transfer

        m2m_changed.connect(
            update_inv_numbers_on_transfer,
            sender=TransferedGoods.inv_numbers.through
        )
