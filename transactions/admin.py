"""
Created by haldunanil on 4/25/2017 per issue #7.
"""
from django.contrib import admin
from transactions.models import CustomerBalance

class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'account_balance', 'timestamp', 'comments',)

admin.site.register(CustomerBalance, CustomerBalanceAdmin)
