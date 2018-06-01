from django.contrib import admin

from .models import (
    Measure,
    Stock,
)


@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'national_symbol', 'key')


admin.site.register(Stock)
