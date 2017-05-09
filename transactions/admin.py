"""
Created by haldunanil on 4/25/2017 per issue #7.
"""
from django.contrib import admin
from transactions.models import CustomerBalance
from transactions.models import Bill
from transactions.models import Charge
from simple_history.admin import SimpleHistoryAdmin


class CustomerBalanceAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'account_balance', 'timestamp')


class BillAdmin(admin.ModelAdmin):
    list_display = ('business', 'customer', 'amount',
                    'timestamp', 'comments')


class BillInline(admin.StackedInline):
    model = Bill
    can_delete = False
    verbose_name_plural = 'bills'
    extra = 1


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'timestamp', 'comments')
    inlines = (BillInline,)


admin.site.register(CustomerBalance, CustomerBalanceAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Charge, ChargeAdmin)
