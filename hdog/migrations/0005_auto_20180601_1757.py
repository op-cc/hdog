# Generated by Django 2.0 on 2018-06-01 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hdog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staff',
            options={'ordering': ('surname',), 'verbose_name': 'сотрудник', 'verbose_name_plural': 'сотрудники'},
        ),
    ]