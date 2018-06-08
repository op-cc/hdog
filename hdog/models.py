from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from categories.models import Category


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


class StorePlace(models.Model):
    @property
    def holder(self):
        try:
            return self.stock
        except ObjectDoesNotExist:
            return self.staff

    def __str__(self):
        return str(self.holder)


class Stock(StorePlace):
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


class Staff(StorePlace):
    surname = models.CharField(verbose_name='фамилия', max_length=30)
    forename = models.CharField(verbose_name='имя', max_length=20)
    patronymic = models.CharField(verbose_name='отчество', max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'сотрудник'
        verbose_name_plural = 'сотрудники'
        ordering = ('surname',)

    def __str__(self):
        result = '{} {}.'.format(self.surname, self.forename[0])

        if self.patronymic:
            result += '{}.'.format(self.patronymic[0])

        return result


class Goods(models.Model):
    category = models.ForeignKey(
        Category,
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
    store_place = models.ForeignKey(
        StorePlace,
        verbose_name='место хранения',
        related_name='goods',
        on_delete=models.CASCADE,
    )

    @property
    def holder(self):
        return self.store_place.holder

    class Meta:
        verbose_name = 'ТМЦ'
        verbose_name_plural = 'ТМЦ'
        unique_together = ('name', 'store_place')

    def __str__(self):
        return '{} ({})'.format(self.name, self.store_place)


class InventoryNumber(models.Model):
    number = models.PositiveIntegerField(verbose_name='инвентарный номер')
    supply = models.ForeignKey(
        Goods,
        verbose_name='ТМЦ',
        related_name='inv_numbers',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'инвентарный номер'
        verbose_name_plural = 'инвентарные номера'

    def __str__(self):
        return str(self.number)


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
        sender_goods = transferred_goods.sender_goods
        recepient_goods = transferred_goods.recepient_goods

        if not sender_goods:
            transfer_type = 'INCOME'
        elif not recepient_goods:
            transfer_type = 'WRITE-OFF'
        else:
            if isinstance(sender_goods.holder, Staff):
                transfer_type = 'RETURN'
            elif isinstance(recepient_goods.holder, Staff):
                transfer_type = 'SUPPLY'
            else:
                transfer_type = 'TRANSFER'

        return transfer_type

    def _get_transfer_participants(self):
        # tg вместо transfered_goods для краткости
        tg = self.goods.all()[0]

        return (
            tg.sender_goods.holder if tg.sender_goods else None,
            tg.recepient_goods.holder if tg.recepient_goods else None,
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
    inv_numbers = models.ManyToManyField(
        InventoryNumber,
        verbose_name='инвентарные номера',
        related_name='transfers',
    )

    class Meta:
        verbose_name = 'перемещенные ТМЦ'
        verbose_name_plural = 'перемещенные ТМЦ'

    def __str__(self):
        return '{quantity} {measure} {name} [{transfer_info}]'.format(**dict(
            quantity=self.quantity,
            measure=self.get_goods_unit().national_symbol,
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

    def get_goods_unit(self):
        return self._get_goods_attribute('unit')

    def save(self, *args, **kwargs):
        new_transfer = False if self.pk else True
        super().save(*args, **kwargs)

        if new_transfer:
            if self.sender_goods:
                self.sender_goods.quantity -= self.quantity
                self.sender_goods.save()
            if self.recepient_goods:
                self.recepient_goods.quantity += self.quantity
                self.recepient_goods.save()

    def create(**kwargs):
        pass
