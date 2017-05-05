"""
Created by haldunanil on 4/30/2017 per issue #7.
"""
import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from transactions.models import CustomerBalance
from transactions.processing import calculate_commission


def get_current_customer_balance(user):
    """
    Get most recent customer balance figure.

    Inputs:
    - user = User object from django.contrib.auth.models

    Returns: most recently created CustomerBalance object for user
    """
    return CustomerBalance.objects \
                          .filter(customer=user) \
                          .latest('timestamp')


def is_current_balance_sufficient(user, amount):
    """
    Check if user's current customer balance is enough to cover a given amount.

    Inputs:
    - user = User object from django.contrib.auth.models
    - amount = float with 2 digits after the decimal point

    Returns: True if current balance is sufficient, False otherwise
    """
    return get_current_customer_balance(user).account_balance >= amount


def add_to_customer_balance(user, amount, comments=None):
    """
    Add given amount to user's current customer balance.

    Conditions:
    - Value for amount must be greater than 0. Otherwise, will raise
      AssertionError

    Inputs:
    - user = User object from django.contrib.auth.models
    - amount = float with 2 digits after the decimal point
    - comments = any comments that might clarify why balance was increased;
                 defaults to None

    Returns: the newly created CustomerBalance object for user
    """
    current_balance = get_current_customer_balance(user).account_balance
    assert amount > 0, "Cannot add a negative number. Use \
        'transactions.functions.reduce_customer_balance' instead."
    return CustomerBalance.objects.create(
        customer=user,
        account_balance=current_balance + amount,
        comments=comments
    )


def reduce_customer_balance(user, amount, comments=None):
    """
    Subtract given amount from user's current customer balance.

    Conditions:
    - Account balance cannot be reduced below 0. Otherwise, will raise
      AssertionError
    - Value for amount must be greater than 0. Otherwise, will raise
      AssertionError

    Inputs:
    - user = User object from django.contrib.auth.models
    - amount = float with 2 digits after the decimal point
    - comments = any comments that might clarify why balance was increased;
                 defaults to None

    Returns: the newly created CustomerBalance object for user
    """
    current_balance = get_current_customer_balance(user).account_balance
    assert current_balance >= amount, "Account balance can't go below $0. \
        Please check your amount and try again."
    assert amount > 0, "Cannot reduce by a negative number. Use \
        'transactions.functions.add_to_customer_balance' instead."
    return CustomerBalance.objects.create(
        customer=user,
        account_balance=current_balance - amount,
        comments=comments
    )


def create_stripe_charge(user, token, total_amount, amount_to_business,
                         business=None, comments=None, *args, **kwargs):
    """

    """
    stripe.api_key = settings.STRIPE_API_SECRET
    # initialize common charge info
    basic_info = {
        amount: total_amount,
        currency: "usd",
        source: token,
        customer: user.profile.stripe_id,
        description: comments
    }

    # if direct payment to business
    if business is not None:
        basic_info['destination'] = {
            "amount": amount_to_business,
            "account": business.stripe_id
        }

    return stripe.Charge.create(**basic_info)
