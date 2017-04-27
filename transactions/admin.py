"""
Created by haldunanil on 4/25/2017 per issue #7.
"""
from django.contrib import admin
from transactions.models import BusinessBalance
from transactions.models import CustomerBalance
from transactions.models import ProcessPayment
from transactions.models import Purchase

class BusinessBalanceAdmin(admin.ModelAdmin):
    list_display = ('business', 'account_balance', 'timestamp', 'comments',)
    verbose_name = 'Business Balance'
    verbose_name_plural = 'Business Balances'

class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'account_balance', 'timestamp', 'comments',)
    verbose_name = 'Customer Balance'
    verbose_name_plural = 'Customer Balances'

class ProcessPaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'payment_amt', 'timestamp', 'comments',)
    verbose_name = 'Stripe Payment'
    verbose_name_plural = 'Stripe Payments'

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'business', 'purchase_amt', 'timestamp',
                    'comments',)
    verbose_name = 'Stripe Payment'
    verbose_name_plural = 'Stripe Payments'

# Register your models here.
admin.site.register(BusinessBalance, BusinessBalanceAdmin)
admin.site.register(CustomerBalance, CustomerBalanceAdmin)
admin.site.register(ProcessPayment, ProcessPaymentAdmin)
admin.site.register(Purchase, PurchaseAdmin)
