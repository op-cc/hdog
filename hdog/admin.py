from django.contrib import admin

from .models import (
    Measure,
    Staff,
    Stock,
)


@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'national_symbol', 'key')


admin.site.register(Stock)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('surname', 'forename', 'patronymic')
