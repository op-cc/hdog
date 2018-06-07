from django.test import TestCase

from .models import (
    Goods,
    Stock,
    Transfer,
    TransferedGoods,
)


class TransferTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        Transfer.objects.create(number=1, comment='income')
        Transfer.objects.create(number=2, comment='second income')
        Transfer.objects.create(number=3, comment='transfer')
        Transfer.objects.create(number=3, comment='second transfer')
        Transfer.objects.create(number=4, comment='supply')
        Transfer.objects.create(number=5, comment='second supply')
        Transfer.objects.create(number=6, comment='return')
        Transfer.objects.create(number=7, comment='write-off')

    def testFirstIncome(self):
        income = Transfer.objects.get(number=1, comment='income')
        cc = Stock.objects.get(code=770)
        grandstream_cc = Goods.objects.get(
            name='Grandstream GXP1615',
            store_place=cc.storeplace_ptr,
        )

        TransferedGoods.create(
            transfer=income,
            recepient_goods=grandstream_cc,
            quantity=10,
            price=11990,
            generate_inv_numbers=True,
        )

        self.assertEqual(grandstream_cc.objects.count(), 10)
        self.assertEqual(grandstream_cc.inv_numbers.count(), 10)
