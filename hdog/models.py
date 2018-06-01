from datetime import date

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Measure(models.Model):
    key = models.PositiveSmallIntegerField(verbose_name='код', unique=True)
    name = models.CharField(verbose_name='наименование', max_length=40, unique=True)
    national_symbol = models.CharField(
        verbose_name='национальное условное обозначение',
        max_length=15,
        unique=True,
    )

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'единицы измерения'

    def __str__(self):
        return self.name


class Stock(models.Model):
    department = models.CharField(
        verbose_name='структурное подразделение',
        max_length=30,
        unique=True,
    )
    code = models.PositiveSmallIntegerField(
        verbose_name='вид деятельности',
        unique=True,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return self.department


class Staff(models.Model):
    surname = models.CharField(verbose_name='фамилия', max_length=30)
    forename = models.CharField(verbose_name='имя', max_length=20)
    patronymic = models.CharField(verbose_name='отчество', max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'сотрудник'
        verbose_name_plural = 'сотрудники'

    def __str__(self):
        result = '{} {}.'.format(self.surname, self.forename[0])

        if self.patronymic:
            result += '{}.'.format(self.patronymic[0])

        return result


class Goods(models.Model):
    category = models.ForeignKey(
        'category.Category',
        verbose_name='категория',
        on_delete=models.CASCADE,
    )
    name = models.CharField(verbose_name='наименование', max_length=150)
    quantity = models.PositiveIntegerField(verbose_name='количество')
    unit = models.ForeignKey(
        Measure,
        verbose_name='единица измерения',
        related_name='+',
        on_delete=models.CASCADE,
    )
    store_place_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    store_place_id = models.PositiveIntegerField()
    store_place = GenericForeignKey('store_place_type', 'store_place_id')

    class Meta:
        verbose_name = 'ТМЦ'
        verbose_name_plural = 'ТМЦ'
        unique_together = ('name', 'store_place_type', 'store_place_id')

    def __str__(self):
        return '{} ({})'.format(self.name, self.store_place)


class InventoryNumber(models.Model):
    number = models.PositiveIntegerField(verbose_name='инвентарный номер')
    supply = models.ForeignKey(
        Goods,
        verbose_name='ТМЦ',
        related_name='inv_numbers',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'инвентарный номер'
        verbose_name_plural = 'инвентарные номера'

    def __str__(self):
        return self.number


class Transfer(models.Model):
    transfer_types = {
        'INCOME': 'Поступление',
        'TRANSFER': 'Перемещение',
        'WRITE-OFF': 'Списание',
        'SUPPLY': 'Выдача',
        'RETURN': 'Возврат',
    }

    date = models.DateField(verbose_name='дата', default=date.today)
    number = models.PositiveSmallIntegerField(verbose_name='номер', blank=True, null=True)
    comment = models.TextField(verbose_name='комментарий')

    class Meta:
        verbose_name = 'перемещение'
        verbose_name_plural = 'перемещения'

    def __str__(self):
        return '{} №{} от {} ({})'.format(
            self.get_transfer_type_str(),
            self.number,
            self.date,
            self.get_transfer_transcript(),
        )

    def _get_transfer_type(self):
        # Берем первый из привязанных ТМЦ, так как в перемещении должен быть хотя бы один ТМЦ
        # и все ТМЦ в перемещении имеют одинаковое место отправления и получения
        transferred_goods = self.goods.all()[0]

        if not transferred_goods.sender_goods:
            transfer_type = 'INCOME'
        elif not transferred_goods.recepient_goods:
            transfer_type = 'WRITE-OFF'
        else:
            sender_model_name = transferred_goods.sender_goods.store_place_type.model
            recepient_model_name = transferred_goods.recepient_goods.store_place_type.model

            if sender_model_name == 'staff':
                transfer_type = 'RETURN'
            elif recepient_model_name == 'staff':
                transfer_type = 'SUPPLY'
            else:
                transfer_type = 'TRANSFER'

        return transfer_type

    def _get_transfer_participants(self):
        # tg вместо transfered_goods для краткости
        tg = self.goods.all()[0]

        return (
            tg.sender_goods.store_place if tg.sender_goods else None,
            tg.recepient_goods.store_place if tg.recepient_goods else None,
        )

    def get_transfer_type_str(self):
        return self.transfer_types[self._get_transfer_type()]

    def get_transfer_transcript(self):
        sender, recepient = self._get_transfer_participants()
        transfer_type = self._get_transfer_type()

        transfer_transcript = ''
        if transfer_type == 'INCOME' or \
           transfer_type == 'WRITE-OFF':
            transfer_transcript = sender if sender else recepient
        else:
            transfer_transcript = '{} ⇒ {}'.format(sender, recepient)

        return transfer_transcript


class TransferedGoods(models.Model):
    transfer = models.ForeignKey(
        Transfer,
        verbose_name='перемещение',
        related_name='goods',
        on_delete=models.CASCADE,
    )
    sender_goods = models.ForeignKey(
        Goods,
        verbose_name='ТМЦ отправителя',
        related_name='sent_goods',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    recepient_goods = models.ForeignKey(
        Goods,
        verbose_name='ТМЦ получателя',
        related_name='received_goods',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name='количество')
    price = models.PositiveIntegerField(verbose_name='цена')
    inv_numbers = models.ManyToManyField(InventoryNumber, verbose_name='инвентарные номера')

    class Meta:
        verbose_name = 'перемещенные ТМЦ'
        verbose_name_plural = 'перемещенные ТМЦ'

    def __str__(self):
        return '{quantity} {measure} {name} [{transfer_info}]'.format(**dict(
            quantity=self.quantity,
            measure=self.get_goods_measure().national_symbol,
            name=self.get_goods_name(),
            transfer_info=self.transfer,
        ))

    def _get_goods_attribute(self, attr_name):
        result = None

        if self.sender_goods:
            result = getattr(self.sender_goods, attr_name)
        else:
            result = getattr(self.recepient_goods, attr_name)

        return result

    def get_goods_name(self):
        return self._get_goods_attribute('name')

    def get_goods_measure(self):
        return self._get_goods_attribute('measure')
