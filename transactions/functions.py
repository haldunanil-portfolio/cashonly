"""
Created by haldunanil on 4/25/2017 per issue #7.
"""
from django.contrib.auth.models import User
from transactions.models import BusinessBalance
from transactions.models import CustomerBalance
from transactions.models import ProcessPayment
from transactions.models import Purchase

def get_current_customer_balance(user):
    """
    Get most recent customer balance figure.

    Inputs:
    - user = User object from django.contrib.auth.models

    Returns: most recently created CustomerBalance object for user
    """
    return CustomerBalance.objects \
                          .filter(customer = user) \
                          .latest('timestamp')

def get_current_business_balance(business):
    """
    Get most recent business balance figure.

    Inputs:
    - business = Businesses object from accounts.models

    Returns: most recently created BusinessBalance object for business
    """
    return BusinessBalance.objects \
                          .filter(business = business) \
                          .latest('timestamp')

def is_current_balance_sufficient(user, amount):
    """
    Check if user's current customer balance is enough to cover a given amount.

    Inputs:
    - user = User object from django.contrib.auth.models
    - amount = float with 2 digits after the decimal point

    Returns: True if current balance is sufficient, False otherwise
    """
    return get_current_balance(user).account_balance >= amount

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
        account_balance=current_balance+amount,
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
        account_balance=current_balance-amount,
        comments=comments
    )

def add_to_business_balance(business, amount, comments=None):
    """
    Add given amount to business' current customer balance.

    Conditions:
    - Value for amount must be greater than 0. Otherwise, will raise
      AssertionError

    Inputs:
    - user = Businesses object from accounts.models
    - amount = float with 2 digits after the decimal point
    - comments = any comments that might clarify why balance was increased;
                 defaults to None

    Returns: the newly created BusinessBalance object for business
    """
    current_balance = get_current_business_balance(business).account_balance
    assert amount > 0, "Cannot add a negative number. Use \
        'transactions.functions.reduce_business_balance' instead."
    return BusinessBalance.objects.create(
        business=business,
        account_balance=current_balance+amount,
        comments=comments
    )

def reduce_business_balance(business, amount, comments=None):
    """
    Subtract given amount from business' current customer balance.

    Conditions:
    - Account balance cannot be reduced below 0. Otherwise, will raise
      AssertionError
    - Value for amount must be greater than 0. Otherwise, will raise
      AssertionError

    Inputs:
    - user = User object from accounts.models
    - amount = float with 2 digits after the decimal point
    - comments = any comments that might clarify why balance was increased;
                 defaults to None

    Returns: the newly created BusinessBalance object for business
    """
    current_balance = get_current_business_balance(business).account_balance
    assert current_balance >= amount, "Account balance can't go below $0. \
        Please check your amount and try again."
    assert amount > 0, "Cannot reduce by a negative number. Use \
        'transactions.functions.add_to_business_balance' instead."
    return BusinessBalance.objects.create(
        business=business,
        account_balance=current_balance-amount,
        comments=comments
    )

def create_purchase_record(user, business, purchase_amt, var_fee_amt,
                           fixed_fee_amt, comments=None):
    """
    Creates a purchase record between a user and a business.

    Conditions:
    - Value for purchase_amt must be greater than 0. Otherwise, will raise
      AssertionError

    Inputs:
    - user =
    - business =
    - purchase_amt =
    - var_fee_amt =
    - fixed_fee_amt =
    - comments =

    Returns: newly created Purchase object
    """
    assert purchase_amt > 0, "Purchase cannot be equal to or less than $0."
    return Purchase.objects.create(
        customer=user,
        business=business,
        purchase_amt=purchase_amt,
        var_fee_amt=var_fee_amt,
        fixed_fee_amt=fixed_fee_amt,
        comments=comments
    )

def create_refund_record(user, business):
    """

    """
    pass
