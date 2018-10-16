from django.forms.widgets import DateInput


class DateDropdownInput(DateInput):
    input_type = 'date'
