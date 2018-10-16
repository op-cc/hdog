from datetime import date as ddate
from decimal import Decimal

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from categories.models import Category

from .widgets import DateDropdownInput
from .models import Measure, Transfer, TransferedGoods


class TransferForm(forms.ModelForm):
    date = forms.DateField(label='Дата', widget=DateDropdownInput, initial=str(ddate.today()))
    number = forms.IntegerField(label='Номер', required=False, min_value=1)
    comment = forms.CharField(
        label='Комментарий',
        required=False,
        widget=forms.widgets.Textarea,
    )

    number.widget.attrs.update(placeholder=number.label)
    comment.widget.attrs.update(placeholder=comment.label)
    comment.widget.attrs.update(rows=3)

    class Meta:
        model = Transfer
        fields = ['date', 'number', 'comment']


class InvNumbersField(forms.CharField):
    def clean(self, value):
        result = super().clean(value)

        inv_numbers_list = []
        if result:
            for s in result.split(','):
                try:
                    if s.find('-') > 0:
                        inv_numbers_range = s.split('-')

                        if len(inv_numbers_range) != 2:
                            raise ValueError

                        range_start = int(inv_numbers_range[0])
                        range_end = int(inv_numbers_range[1])

                        if range_start > range_end:
                            raise ValueError

                        inv_numbers_list += range(range_start, range_end + 1)
                    else:
                        inv_numbers_list += [int(s)]
                except ValueError:
                    raise forms.ValidationError('Неверный формат инвентарных номеров')

        # Убираем дупликаты
        return list(set(inv_numbers_list))


class GoodsRowForm(forms.Form):
    category = forms.ModelChoiceField(label='Категория', queryset=Category.objects.all())
    goods = forms.CharField(label='ТМЦ', min_length=1)
    quantity = forms.IntegerField(label='Количество', initial=1, min_value=1)
    measure = forms.ModelChoiceField(label='Единица измерения', queryset=Measure.objects.all())
    price = forms.DecimalField(
        label='Цена',
        min_value=Decimal(0.01),
        decimal_places=2,
    )
    generate_inv_numbers = forms.BooleanField(
        label='Сгенерировать инвентарные номера',
        required=False
    )
    inv_numbers = InvNumbersField(label='Инвентарные номера', required=False)

    sender = None
    recepient = None
    transfer = None

    price.widget.attrs.update(placeholder=price.label)
    inv_numbers.widget.attrs.update(placeholder=inv_numbers.label)
    goods.widget.attrs.update(placeholder=goods.label)
    goods.widget.attrs.update(list='goods')

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        transfer_create_args = {
            'transfer': self.transfer,
            'sender': self.sender,
            'recepient': self.recepient,
            'goods_name': cleaned_data.get('goods', None),
            'price': cleaned_data['price'],
            'quantity': cleaned_data['quantity'],
            'generate_inv_numbers': cleaned_data['generate_inv_numbers'],
            'inv_numbers': cleaned_data['inv_numbers'],
            'category': cleaned_data['category'],
            'measure': cleaned_data['measure'],
            'simulate': True,
        }

        try:
            TransferedGoods.create(**transfer_create_args)
        except (ObjectDoesNotExist, RuntimeError, ValueError) as e:
            raise forms.ValidationError(str(e))

        return cleaned_data


GoodsRowFormSet = forms.formset_factory(GoodsRowForm)
