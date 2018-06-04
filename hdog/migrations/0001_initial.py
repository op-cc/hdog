# Generated by Django 2.0 on 2018-06-04 19:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0002_auto_20170217_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='наименование')),
                ('quantity', models.PositiveIntegerField(verbose_name='количество')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.Category', verbose_name='категория')),
            ],
            options={
                'verbose_name': 'ТМЦ',
                'verbose_name_plural': 'ТМЦ',
            },
        ),
        migrations.CreateModel(
            name='InventoryNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='инвентарный номер')),
                ('supply', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inv_numbers', to='hdog.Goods', verbose_name='ТМЦ')),
            ],
            options={
                'verbose_name': 'инвентарный номер',
                'verbose_name_plural': 'инвентарные номера',
            },
        ),
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.PositiveSmallIntegerField(unique=True, verbose_name='код')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='наименование')),
                ('national_symbol', models.CharField(max_length=15, unique=True, verbose_name='национальное условное обозначение')),
            ],
            options={
                'verbose_name': 'единица измерения',
                'verbose_name_plural': 'единицы измерения',
            },
        ),
        migrations.CreateModel(
            name='StorePlace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='дата')),
                ('number', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='номер')),
                ('comment', models.TextField(verbose_name='комментарий')),
            ],
            options={
                'verbose_name': 'перемещение',
                'verbose_name_plural': 'перемещения',
            },
        ),
        migrations.CreateModel(
            name='TransferedGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='количество')),
                ('price', models.PositiveIntegerField(verbose_name='цена')),
                ('inv_numbers', models.ManyToManyField(related_name='transfers', to='hdog.InventoryNumber', verbose_name='инвентарные номера')),
                ('recepient_goods', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_goods', to='hdog.Goods', verbose_name='ТМЦ получателя')),
                ('sender_goods', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_goods', to='hdog.Goods', verbose_name='ТМЦ отправителя')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods', to='hdog.Transfer', verbose_name='перемещение')),
            ],
            options={
                'verbose_name': 'перемещенные ТМЦ',
                'verbose_name_plural': 'перемещенные ТМЦ',
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('storeplace_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hdog.StorePlace')),
                ('surname', models.CharField(max_length=30, verbose_name='фамилия')),
                ('forename', models.CharField(max_length=20, verbose_name='имя')),
                ('patronymic', models.CharField(blank=True, max_length=30, null=True, verbose_name='отчество')),
            ],
            options={
                'verbose_name': 'сотрудник',
                'verbose_name_plural': 'сотрудники',
            },
            bases=('hdog.storeplace',),
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('storeplace_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hdog.StorePlace')),
                ('department', models.CharField(max_length=30, unique=True, verbose_name='структурное подразделение')),
                ('code', models.PositiveSmallIntegerField(blank=True, null=True, unique=True, verbose_name='вид деятельности')),
            ],
            options={
                'verbose_name': 'склад',
                'verbose_name_plural': 'склады',
            },
            bases=('hdog.storeplace',),
        ),
        migrations.AddField(
            model_name='goods',
            name='store_place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods', to='hdog.StorePlace', verbose_name='место хранения'),
        ),
        migrations.AddField(
            model_name='goods',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='hdog.Measure', verbose_name='единица измерения'),
        ),
        migrations.AlterUniqueTogether(
            name='goods',
            unique_together={('name', 'store_place')},
        ),
    ]
