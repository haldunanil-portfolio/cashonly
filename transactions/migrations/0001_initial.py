# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 22:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0013_auto_20170425_1804'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Business_Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Businesses')),
            ],
        ),
        migrations.CreateModel(
            name='Customer_Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Process_Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_amt', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Purchase Amount')),
                ('var_comm_amt', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Variable Commission Amt')),
                ('fixed_comm_amt', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Fixed Commission Amt')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comments', models.CharField(blank=True, max_length=255, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_amt', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Purchase Amount')),
                ('var_fee_amt', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Variable Fee Amt')),
                ('fixed_fee_amt', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Fixed Fee Amt')),
                ('refund', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comments', models.CharField(blank=True, max_length=255, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Businesses')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
