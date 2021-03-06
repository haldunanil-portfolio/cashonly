from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from appconfig.functions import get_value


class BusinessType(models.Model):
    """
    Contains information on business type (i.e. industry)
    """
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Business Type'
        verbose_name_plural = 'Business Types'

    def __str__(self):
        return u'%s' % (self.name)


class Businesses(models.Model):
    """
    Contain information for individual businesses registered with Cash Only
    """
    name = models.CharField(max_length=100)
    business_type = models.ForeignKey(BusinessType, on_delete=models.SET_NULL,
                                      null=True)
    website = models.URLField(blank=True, null=True)
    yelp_page = models.URLField(blank=True, null=True)
    facebook_page = models.URLField(blank=True, null=True)
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
        default=0.5
    )
    tips_allowed = models.BooleanField(default=True)
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
