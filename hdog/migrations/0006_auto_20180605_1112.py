# Generated by Django 2.0 on 2018-06-05 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hdog', '0005_auto_20180601_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorynumber',
            name='supply',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inv_numbers', to='hdog.Goods', verbose_name='ТМЦ'),
        ),
    ]
