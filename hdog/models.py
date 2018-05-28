from django.db import models


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


class Stock(models.Model):
    department = models.CharField(
        verbose_name='структурное подразделение',
        max_length=30,
        unique=True,
    )

    class Meta:
        verbose_name = 'склад'
        verbose_name_plural = 'склады'
