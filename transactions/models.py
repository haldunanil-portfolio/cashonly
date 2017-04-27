"""
Created by haldunanil on 4/25/2017 per issue #7.
"""
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Businesses
from django.core.validators import MinValueValidator

class ProcessPayment(models.Model):
    """

    """
    customer = models.ForeignKey(User)
    payment_amt = models.DecimalField(max_digits=10, decimal_places=2,
                                       verbose_name='Purchase Amount',
                                       validators=[MinValueValidator(0)])
    var_comm_amt = models.DecimalField(max_digits=10, decimal_places=2,
                                  verbose_name='Variable Commission Amt',
                                  blank=True, null=True,
                                  validators=[MinValueValidator(0)])
    fixed_comm_amt = models.DecimalField(max_digits=10, decimal_places=2,
                                  verbose_name='Fixed Commission Amt',
                                  blank=True, null=True,
                                  validators=[MinValueValidator(0)])
    token = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u'A Stripe payment of %s was processed on %s for %s.' % (
            self.payment_amt, self.timestamp, self.customer
        )

class Purchase(models.Model):
    """

    """
    customer = models.ForeignKey(User)
    business = models.ForeignKey(Businesses)
    purchase_amt = models.DecimalField(max_digits=10, decimal_places=2,
                                       verbose_name='Purchase Amount',
                                       validators=[MinValueValidator(0)])
    var_fee_amt = models.DecimalField(max_digits=10, decimal_places=2,
                                  verbose_name='Variable Fee Amt',
                                  blank=True, null=True,
                                  validators=[MinValueValidator(0)])
    fixed_fee_amt = models.DecimalField(max_digits=10, decimal_places=2,
                                  verbose_name='Fixed Fee Amt',
                                  blank=True, null=True,
                                  validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u'%s: $%s at %s on %s.' % (
            self.customer, self.purchase_amt, self.business, self.timestamp
        )

class CustomerBalance(models.Model):
    """

    """
    customer = models.ForeignKey(User)
    account_balance = models.DecimalField(max_digits=10,
                                          decimal_places=2,
                                          default=0,
                                          validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u'%s had a balance of %s on %s.' % (
            self.customer, self.account_balance, self.timestamp
        )

class BusinessBalance(models.Model):
    """

    """
    business = models.ForeignKey(Businesses)
    account_balance = models.DecimalField(max_digits=10,
                                          decimal_places=2,
                                          default=0,
                                          validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u'%s had a balance of %s on %s.' % (
            self.business, self.account_balance, self.timestamp
        )
