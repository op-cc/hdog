from datetime import date
from typing import List, Tuple

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max, Q, QuerySet

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
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)
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
        return '{}'.format(self.name)


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

    def generate(quantity: int) -> QuerySet:
        if quantity <= 0:
            raise ValueError('Количество генерируемых инвентарных номеров должно быть больше нуля')

        start_number = settings.BASE_INV_NUMBER

        if InventoryNumber.objects.all():
            max_number = InventoryNumber.objects.all().aggregate(Max('number'))
            start_number = max_number['number__max'] + 1

        generated_range = range(start_number, start_number + quantity)
        for number in generated_range:
            InventoryNumber.objects.create(number=number)

        return InventoryNumber.objects.filter(number__in=generated_range)


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
    comment = models.TextField(verbose_name='комментарий', blank=True, null=True)

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

    def _transferBaseChecks(sender: StorePlace, recepient: StorePlace,
                            quantity: int, price: int):
        if quantity <= 0:
            raise ValueError('Количество перемещаемых ТМЦ должно быть больше нуля')
        if price <= 0:
            raise ValueError('Цена должна быть положительным числом')
        if not sender and not recepient:
            raise ValueError('Укажите отправителя и/или получателя')
        if not sender and type(recepient.holder) == Staff:
            raise ValueError('Нельзя оформить поступление на сотрудника')

    def _clearInvNumbers(sender: StorePlace, recepient: StorePlace,
                         goods_name: str, sender_goods: Goods, recepient_goods: Goods,
                         quantity: int, inv_numbers: List[int], inv_numbers_qs: QuerySet,
                         generate_inv_numbers: bool) -> QuerySet:
        """
        Функция возвращает набор перемещаемых инвентарных номеров
        """
        if generate_inv_numbers and (inv_numbers or inv_numbers_qs):
            raise RuntimeError('Нельзя одновременно использовать заданные '
                               'инвентарные номера и сгенерированные'
                               )

        result_inv_numbers_qs, inv_numbers_created = TransferedGoods._getInvNumbersQS(
            generate_inv_numbers, quantity, inv_numbers, inv_numbers_qs
        )

        all_goods_with_target_name = Goods.objects.filter(name=goods_name)
        inv_numbers_for_all_target_goods = InventoryNumber.objects.filter(
            supply__in=all_goods_with_target_name
        )

        if not result_inv_numbers_qs and inv_numbers_for_all_target_goods.count() > 0:
            raise ValueError('Укажите инвентарные номера')

        try:
            inv_numbers_count = len(result_inv_numbers_qs)

            if not generate_inv_numbers and \
               not inv_numbers_count == 0 and \
               inv_numbers_count < quantity:
                raise ValueError('Количество инвентарных номеров должно совпадать '
                                 'с количеством перемещаемых ТМЦ'
                                 )

            if result_inv_numbers_qs and \
               inv_numbers_for_all_target_goods.count() == 0 and \
               recepient_goods.quantity > 0:
                raise ValueError('Данному ТМЦ ранее не присваивались инвентарные номера')
        except ValueError as e:
            if inv_numbers_created:
                result_inv_numbers_qs.delete()
            raise e

        if not sender and not inv_numbers_created and result_inv_numbers_qs:
            if InventoryNumber.objects.filter(pk__in=result_inv_numbers_qs):
                raise ValueError('Указанные инвентарные номера уже заняты')

        if sender and result_inv_numbers_qs:
            matching_inv_numbers_qs = InventoryNumber.objects.filter(
                Q(supply=sender_goods) &
                Q(pk__in=result_inv_numbers_qs)
            ).count()

            if matching_inv_numbers_qs.count() != result_inv_numbers_qs.count():
                raise ValueError('Указанные инвентарные номера не привязаны к ТМЦ отправителя')

        return result_inv_numbers_qs

    def _getInvNumbersQS(generate_inv_numbers: bool, quantity: int, inv_numbers: List[int],
                         inv_numbers_qs: QuerySet) -> Tuple[QuerySet, bool]:
        result = []
        res_created = False

        if generate_inv_numbers:
            result = InventoryNumber.generate(quantity)
            res_created = True
        elif inv_numbers:
            result = InventoryNumber.objects.filter(number__in=inv_numbers)
            if result.count() == 0:
                for number in inv_numbers:
                    InventoryNumber.objects.create(number=number)

                res_created = True
            elif result.count() < len(inv_numbers):
                raise ValueError('Указанные инвентарные номера не существуют')
        elif inv_numbers_qs:
            result = inv_numbers_qs

        return result, res_created

    def create(transfer: Transfer, goods_name: str, price: int, quantity: int,
               sender: StorePlace = None, recepient: StorePlace = None,
               inv_numbers: List[int] = None, inv_numbers_qs: QuerySet = None,
               generate_inv_numbers: bool = False, category: Category = None,
               measure: Measure = None, simulate: bool = False,
               ) -> 'TransferedGoods':
        """
        Создание пункта перемещения после выполнения всех проверок на ошибки
        Возможные исключения: ObjectDoesNotExist, RuntimeError, ValueError
        """
        sender_goods = None
        recepient_goods = None
        if recepient:
            try:
                existing_goods = Goods.objects.filter(
                    name=goods_name,
                )[0]
                if existing_goods.unit != measure:
                    raise ValueError(
                        'ТМЦ с данным наименованием должно иметь единицу измерения {}'.format(
                            existing_goods.unit
                        )
                    )
                elif existing_goods.category != category:
                    raise ValueError(
                        'ТМЦ с данным наименованием должно иметь категорию {}'.format(
                            existing_goods.category
                        )
                    )
            except IndexError:
                pass

            recepient_goods, _ = Goods.objects.get_or_create(
                name=goods_name,
                store_place=recepient,
                category=category,
                unit=measure,
            )
        if sender:
            try:
                sender_goods = Goods.objects.get(name=goods_name, store_place=sender)

                if sender_goods.quantity < quantity:
                    raise ValueError('У отправителя недостаточно ТМЦ для выполнения операции')
            except ObjectDoesNotExist as e:
                raise e('У отправителя нет этого ТМЦ')

            if generate_inv_numbers:
                raise ValueError('Нельзя генерировать инвентарные номера для ТМЦ, '
                                 'которые уже есть в базе данных')

        TransferedGoods._transferBaseChecks(sender, recepient_goods, quantity, price)

        clear_inv_numbers_qs = TransferedGoods._clearInvNumbers(
            sender,
            recepient,
            goods_name,
            sender_goods,
            recepient_goods,
            quantity,
            inv_numbers,
            inv_numbers_qs,
            generate_inv_numbers,
        )

        if simulate:
            if clear_inv_numbers_qs:
                clear_inv_numbers_qs.delete()

        """
        Выполнение операции
        """
        transfered_goods = None

        if not simulate:
            transfered_goods = TransferedGoods.objects.create(
                transfer=transfer,
                sender_goods=sender_goods,
                recepient_goods=recepient_goods,
                quantity=quantity,
                price=price,
            )

            if sender:
                sender_goods.quantity -= quantity
                sender_goods.save()
            if recepient:
                recepient_goods.quantity += quantity
                recepient_goods.save()

                if clear_inv_numbers_qs:
                    clear_inv_numbers_qs.update(supply=recepient_goods)
                    transfered_goods.inv_numbers.set(list(clear_inv_numbers_qs))

        return transfered_goods
