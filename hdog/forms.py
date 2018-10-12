from datetime import date as ddate

from django import forms

from categories.models import Category

from .widgets import DateDropdownInput
from .models import Measure, Transfer


class TransferForm(forms.ModelForm):
    date = forms.DateField(label='Дата', widget=DateDropdownInput, initial=str(ddate.today()))
    number = forms.IntegerField(label='Номер', required=False, min_value=1)
    comment = forms.CharField(label='Комментарий', widget=forms.widgets.Textarea)

    number.widget.attrs.update(placeholder=number.label)
    comment.widget.attrs.update(placeholder=comment.label)
    comment.widget.attrs.update(rows=3)

    class Meta:
        model = Transfer
        fields = ['date', 'number', 'comment']



class InvNumbersField(forms.CharField):
    def clean(self, value):
        result = super().clean(value)

        if result:
            result = [int(inv_number.strip()) for inv_number in result.split(',')]

        return result


class GoodsRowForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    goods = forms.CharField(label='ТМЦ')
    quantity = forms.IntegerField(label='Количество', initial=1, min_value=1)
    measure = forms.ModelChoiceField(queryset=Measure.objects.all())
    price = forms.IntegerField(label='Цена', initial=0, min_value=0)
    generate_inv_numbers = forms.BooleanField(
        label='Сгенерировать инвентарные номера',
        required=False
    )
    inv_numbers = InvNumbersField(label='Инвентарные номера', required=False)


GoodsRowFormSet = forms.formset_factory(GoodsRowForm)
