"""
Created by haldunanil on 4/25/2017 per issue #7.

Commented out for now, maybe reenabled for future data validation/analytics
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class CustomerBalance(models.Model):
    """
    Represent the customer balance of a user at a given point in time.
    """
    customer = models.ForeignKey(User)
    account_balance = models.IntegerField(default=0,
                                          validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u'%s had a balance of %s on %s.' % (
            self.customer, self.account_balance, self.timestamp
        )
