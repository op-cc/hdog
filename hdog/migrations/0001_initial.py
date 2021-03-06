# Generated by Django 2.0 on 2018-05-28 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.PositiveSmallIntegerField(verbose_name='код')),
                ('name', models.CharField(max_length=40, verbose_name='наименование')),
                ('national_symbol', models.CharField(max_length=15, verbose_name='национальное условное обозначение')),
            ],
            options={
                'verbose_name': 'единица измерения',
                'verbose_name_plural': 'единицы измерения',
            },
        ),
    ]
