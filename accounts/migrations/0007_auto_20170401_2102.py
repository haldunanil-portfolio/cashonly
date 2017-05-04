# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 01:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20170401_2056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='businesses',
            old_name='state_province',
            new_name='state',
        ),
        migrations.AlterField(
            model_name='businesses',
            name='address_2',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='businesses',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]
