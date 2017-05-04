from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class Businesses(models.Model):
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
    country = CountryField()
    tax_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u'%s' % (self.name)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    business = models.ForeignKey(Businesses, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_customer_id = models.CharField(max_length=30, blank=True, null=True)
