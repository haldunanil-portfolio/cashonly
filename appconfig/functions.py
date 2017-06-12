"""
Created by haldunanil on 5/1/2017 per issue #7.
"""
from appconfig.models import Config

def get_value(key):
    """
    Get value for any key in app config
    """
    return Config.objects.get(key=key).get_value()
