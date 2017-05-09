"""
Created by haldunanil on 5/5/2017 per issue #7.
"""
from django.contrib import admin
from appconfig.models import Config
from simple_history.admin import SimpleHistoryAdmin

class ConfigAdmin(SimpleHistoryAdmin):
    list_display = ('key', 'comments', 'value',)

admin.site.register(Config, ConfigAdmin)
