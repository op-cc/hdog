from django.contrib import admin

from .models import (
    Goods,
    InventoryNumber,
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


class InventoryNumbersInline(admin.StackedInline):
    model = InventoryNumber
    extra = 0


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    inlines = [
        InventoryNumbersInline,
    ]
