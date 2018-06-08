from django.test import TestCase

from .models import (
    Goods,
    Staff,
    Stock,
    Transfer,
    TransferedGoods,
)


class TransferTestCase(TestCase):
    fixtures = ['test_data.json']

    gs_first_income_count = 10
    gs_second_income_count = 5
    gs_transfer_count = 4
    gs_second_transfer_count = 3
    gs_supply_count = 1
    gs_second_supply_count = 2
    gs_return_count = 1
    gs_write_off_count = 3
    gs_second_income_inv_numbers = [x for x in range(770770, 770770 + gs_second_income_count)]

    screws_first_income_count = 100
    screws_second_income_count = 50
    screws_supply_count = 30
    screws_second_supply_count = 40
    screws_return_count = 20
    screws_write_off_count = 90
    screws_second_income_inv_numbers = [x for x in range(1, 1 + screws_second_income_count)]

    def setUp(self):
        Transfer.objects.create(number=1, comment='income')
        Transfer.objects.create(number=2, comment='second income')
        Transfer.objects.create(number=3, comment='transfer')
        Transfer.objects.create(number=3, comment='second transfer')
        Transfer.objects.create(number=4, comment='supply')
        Transfer.objects.create(number=5, comment='second supply')
        Transfer.objects.create(number=6, comment='return')
        Transfer.objects.create(number=7, comment='write-off')

    def test_010_firstIncome(self):
        income = Transfer.objects.get(number=1, comment='income')
        cc = Stock.objects.get(code=770).storeplace_ptr
        ivanov = Staff.objects.get(surname='Иванов').storeplace_ptr

        """
        Инициализация аргументов
        """
        base_create_args = {
            'transfer': income,
            'recepient': cc,
        }

        gs_base_args = {
            **base_create_args,
            'goods_name': 'Grandstream GXP1615',
            'price': 11990,
            'quantity': self.gs_first_income_count,
            'generate_inv_numbers': True,
        }
        gs_invalid_quantity_args = {
            **gs_base_args,
            'quantity': 0,
        }
        gs_invalid_price_args = {
            **gs_base_args,
            'price': 0,
        }
        gs_no_stores_args = {
            **gs_base_args,
            'recepient': None,
        }

        screws_base_args = {
            **base_create_args,
            'goods_name': 'Шурупы',
            'price': 3,
            'quantity': self.screws_first_income_count,
        }
        screws_invalid_recepient_args = {
            **screws_base_args,
            'recepient': ivanov,
        }

        """
        Проверка исключений
        """
        self.assertRaisesRegex(
            ValueError,
            'Количество перемещаемых ТМЦ должно быть больше нуля',
            TransferedGoods.create,
            **gs_invalid_quantity_args,
        )
        self.assertRaisesRegex(
            ValueError,
            'Укажите отправителя и/или получателя',
            TransferedGoods.create,
            **gs_no_stores_args,
        )
        self.assertRaisesRegex(
            ValueError,
            'Цена должна быть положительным числом',
            TransferedGoods.create,
            **gs_invalid_price_args,
        )

        self.assertRaisesRegex(
            ValueError,
            'Нельзя оформить поступление на сотрудника',
            TransferedGoods.create,
            **screws_invalid_recepient_args,
        )

        """
        Проверка создания поступления
        """
        TransferedGoods.create(**gs_base_args)
        TransferedGoods.create(**screws_base_args)

        grandstream_cc = Goods.objects.get(
            name='Grandstream GXP1615',
            store_place=cc,
        )
        screws_cc = Goods.objects.get(
            name='Шурупы',
            store_place=cc,
        )

        self.assertEqual(grandstream_cc.quantity, self.gs_first_income_count)
        self.assertEqual(grandstream_cc.inv_numbers.count(), self.gs_first_income_count)
        self.assertEqual(screws_cc.quantity, self.screws_first_income_count)
        self.assertEqual(screws_cc.inv_numbers.count(), self.screws_first_income_count)

    def test_020_secondIncome(self):
        second_income = Transfer.objects.get(number=2, comment='second income')
        cc = Stock.objects.get(code=770).storeplace_ptr
        grandstream_cc = Goods.objects.get(
            name='Grandstream GXP1615',
            store_place=cc,
        )

        """
        Инициализация аргументов
        """
        base_create_args = {
            'transfer': second_income,
            'recepient': cc,
        }

        gs_base_args = {
            **base_create_args,
            'goods_name': 'Grandstream GXP1615',
            'price': 11990,
            'quantity': self.gs_second_income_count,
            'inv_numbers': self.gs_second_income_inv_numbers,
        }
        gs_invalid_inv_numbers = {
            **gs_base_args,
            'inv_numbers': [self.gs_second_income_inv_numbers[0]]
        }
        gs_no_inv_numbers = {
            **gs_base_args,
            'inv_numbers': None,
        }
        gs_used_inv_numbers = {
            **gs_base_args,
            'inv_numbers_qs': grandstream_cc.inv_numbers.all()[:self.gs_second_income_count]
        }

        screws_base_args = {
            **base_create_args,
            'goods_name': 'Шурупы',
            'price': 3,
            'quantity': self.screws_second_income_count,
        }
        screws_with_inv_numbers = {
            **screws_base_args,
            'inv_numbers': self.screws_second_income_inv_numbers,
        }

        """
        Проверка исключений
        """
        self.assertRaisesRegex(
            ValueError,
            'Количество инвентарных номеров должно совпадать с количеством перемещаемых ТМЦ',
            TransferedGoods.create,
            **gs_invalid_inv_numbers,
        )
        self.assertRaisesRegex(
            ValueError,
            'Укажите инвентарные номера',
            TransferedGoods.create,
            **gs_no_inv_numbers,
        )
        self.assertRaisesRegex(
            ValueError,
            'Указанные инвентарные номера уже заняты',
            TransferedGoods.create,
            **gs_used_inv_numbers,
        )

        self.assertRaisesRegex(
            ValueError,
            'Данному ТМЦ ранее не присваивались инвентарные номера',
            TransferedGoods.create,
            **screws_with_inv_numbers,
        )

        """
        Проверка создания поступления
        """
        TransferedGoods.create(**gs_base_args)
        TransferedGoods.create(**screws_base_args)

        grandstream_cc.refresh_from_db()
        screws_cc = Goods.objects.get(
            name='Шурупы',
            store_place=cc,
        )

        gs_total_count = self.gs_first_income_count + self.gs_second_income_count
        screws_total_count = self.screws_first_income_count + self.screws_second_income_count

        self.assertEqual(grandstream_cc.quantity, gs_total_count)
        self.assertEqual(grandstream_cc.inv_numbers.count(), gs_total_count)
        self.assertEqual(screws_cc.quantity, screws_total_count)
        self.assertEqual(screws_cc.inv_numbers.count(), screws_total_count)
