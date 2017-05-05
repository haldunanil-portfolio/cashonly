"""
Created by haldunanil on 4/25/2017 per issue #7.

Commented out for now, maybe reenabled for future data validation/analytics
"""
from django.contrib import admin
from transactions.models import CustomerBalance

class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'account_balance', 'timestamp', 'comments',)
    verbose_name = 'Customer Balance'
    verbose_name_plural = 'Customer Balances'

admin.site.register(CustomerBalance, CustomerBalanceAdmin)
