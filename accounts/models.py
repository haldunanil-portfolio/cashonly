from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from appconfig.functions import get_value


class Businesses(models.Model):
    """
    Contain information for individual businesses registered with Cash Only
    """
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True,
                              null=True)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50,
                                 blank=True)
    city = models.CharField(max_length=60)
    state_province = models.CharField(max_length=30,
                                      verbose_name='State',
                                      null=True)
    zipcode = models.CharField(max_length=5)
    country = CountryField()
    rev_share_perc = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Revenue Share %',
        default=get_value("DEFAULT_REV_SHARE")
    )
    stripe_id = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return u'%s' % (self.name)

class Profile(models.Model):
    """
    Contains additional profile information on users beyond the standard
    Django User class
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    stripe_id = models.CharField(max_length=30, blank=True, null=True)
    business = models.ForeignKey(Businesses, on_delete=models.SET_NULL,
                                 blank=True, null=True)
