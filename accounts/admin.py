from django.contrib import admin
from .models import Businesses, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

## extending base user class
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

## adding additional sections to admin
class BusinessesAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'city', 'state_province', 'country')

admin.site.register(Businesses, BusinessesAdmin)
