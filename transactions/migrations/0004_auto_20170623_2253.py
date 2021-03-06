# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-24 02:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20170518_1825'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bill',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Bill', 'verbose_name_plural': 'Bills'},
        ),
        migrations.AddField(
            model_name='bill',
            name='large_party',
            field=models.BooleanField(default=False),
        ),
    ]
