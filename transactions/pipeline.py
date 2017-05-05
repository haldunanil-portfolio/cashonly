"""
Created by haldunanil on 4/27/2017 per issue #7.
"""


def PurchaseFromBalance(user, business, amount, var_fee_amt):
    """
    """
    # 1) check if balance sufficient
    # 2) if yes:
    #   a)
    # 3) if no: raise ValueError


def PayAsYouGo():
    """
    """
    # placeholder to charge to stripe
    #


def AddToBalance():
    """
    """
    # placeholder to charge to stripe
    #


## testing
from django.contrib.auth.models import User
from accounts.models import Businesses

user = User.objects.get(username='haldunanil')
biz = Businesses.objects.get(name='Cash Only')
