"""
Created by haldunanil on 4/25/2017 per issue #7.
"""
from django.contrib import admin
from transactions.models import CustomerBalance
from simple_history.admin import SimpleHistoryAdmin


class CustomerBalanceAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'account_balance', 'timestamp')

admin.site.register(CustomerBalance, CustomerBalanceAdmin)
