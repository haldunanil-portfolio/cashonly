from django.contrib import admin
from .models import Businesses, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib import admin
from django import forms
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE
from transactions.models import CustomerBalance


## extending base user class
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class CustomerBalanceInline(admin.StackedInline):
    model = CustomerBalance
    can_delete = False
    verbose_name_plural = 'customer balances'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, CustomerBalanceInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

## adding additional sections to admin
class BusinessesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'website', 'city', 'state_province', 'country',
    )

class FlatPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = FlatPage
        fields = '__all__'

class PageAdmin(FlatPageAdmin):
    """
    Page Admin
    """
    form = FlatPageForm

admin.site.register(Businesses, BusinessesAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)
