"""
Created by haldunanil on 4/25/2017 per issue #7.

Commented out for now, maybe reenabled for future data validation/analytics
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords
from django.conf import settings


class CustomerBalance(models.Model):
    """
    Represent the customer balance of a user at a given point in time.
    """
    customer = models.OneToOneField(User, primary_key=True, db_index=True)
    account_balance = models.IntegerField(default=0,
                                          validators=[MinValueValidator(0)],
                                          verbose_name="Account balance (in cents)")
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Customer Balance'
        verbose_name_plural = 'Customer Balances'

    def __str__(self):
        return u'%s has a balance of $%s.' % (
            self.customer, self.account_balance / 100
        )

    def get_current_customer_balance(self):
        """
        Get most recent customer balance figure.

        Inputs:
        - user = User object from django.contrib.auth.models

        Returns: most recently created CustomerBalance object for user
        """
        return self.account_balance

    def is_current_balance_sufficient(self, amount):
        """
        Check if current customer balance is enough to cover a given amount.

        Inputs:
        - amount = float with 2 digits after the decimal point

        Returns: True if current balance is sufficient, False otherwise
        """
        return self.account_balance >= amount

    def add_to_customer_balance(self, amount):
        """
        Add given amount to user's current customer balance.

        Conditions:
        - Value for amount must be greater than 0. Otherwise, will raise
          AssertionError

        Inputs:
        - amount = float with 2 digits after the decimal point

        Returns: the newly created CustomerBalance object for user
        """
        assert amount > 0, "Cannot add a negative number. Use \
            'transactions.functions.reduce_customer_balance' instead."

        self.account_balance += amount

        return self.account_balance

    def reduce_customer_balance(self, amount):
        """
        Subtract given amount from user's current customer balance.

        Conditions:
        - Account balance cannot be reduced below 0. Otherwise, will raise
          AssertionError
        - Value for amount must be greater than 0. Otherwise, will raise
          AssertionError

        Inputs:
        - amount = float with 2 digits after the decimal point

        Returns: the newly created CustomerBalance object for user
        """
        assert self.is_current_balance_sufficient(), "Account balance can't go below $0. \
            Please check your amount and try again."
        assert amount > 0, "Cannot reduce by a negative number. Use \
            'transactions.functions.add_to_customer_balance' instead."

        if self.is_current_balance_sufficient:
            self.account_balance -= amount

        return self.account_balance
