# Generated by Django 2.0 on 2018-06-15 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hdog', '0006_auto_20180605_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='количество'),
        ),
    ]