# Generated by Django 2.0 on 2018-06-01 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hdog', '0003_auto_20180601_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorynumber',
            name='supply',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inv_numbers', to='hdog.Goods', verbose_name='ТМЦ'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='number',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='номер'),
        ),
    ]
