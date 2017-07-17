"""
Created by haldunanil on 5/1/2017 per issue #7.
"""
import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from transactions.models import CustomerBalance
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from accounts.models import Profile


def create_customer_stripe_account(user, commit=True, *args, **kwargs):
    """
    Create a stripe Customer account for a user.

    Inputs:
    - user = User instance from django.contrib.auth.models

    Returns: created Stripe Customer object
    """
    # create account on stripe
    stripe.api_key = settings.STRIPE_API_SECRET
    customer = stripe.Customer.create(
        email=user.email,
        metadata={
            "user_id": user.id
        }
    )

    # add user to default subscription
    stripe.Subscription.create(
        customer=customer,
        plan="basic"
    )

    # record stripe id to backend
    if commit:
        user.profile.stripe_id = customer.id
        user.profile.save()

    return customer


def create_managed_stripe_account(user, business, *args, **kwargs):
    """
    """
    # create managed account on stripe
    stripe.api_key = settings.STRIPE_API_SECRET
    account = stripe.Account.create(
        country="US",
        type="custom",
        business_name=business.name,
        email=user.email,
        legal_entity={
            "address": {
                "city": business.city,
                "country": business.country,
                "line1": business.address_1,
                "line2": business.address_2,
                "postal_code": business.zipcode,
                "state": business.state_province
            },
            "first_name": user.first_name,
            "last_name": user.last_name,
            "type": "company"
        }
    )

    # associate stripe id with our backend
    business.stripe_id = account.id
    business.save()

    return account


def update_managed_stripe_account(user, *args, **kwargs):
    """
    """
    # update managed account on stripe
    stripe.api_key = settings.STRIPE_API_SECRET
    account = stripe.Account.retrieve(user.profile.business.stripe_id)
    account.business_name = business.name
    account.legal_entity = {
        "address": {
            "city": business.city,
            "country": business.country,
            "line1": business.address_1,
            "line2": business.address_2,
            "postal_code": business.zipcode,
            "state": business.state_province
        },
        "first_name": user.first_name,
        "last_name": user.last_name,
        "type": "company"
    }
    account.save()



@receiver(pre_delete, sender=Profile)
def model_pre_delete(sender, instance, **kwargs):
    """
    Delete associated stripe account
    """
    stripe.api_key = settings.STRIPE_API_SECRET
    cust = stripe.Customer.retrieve(instance.stripe_id)
    cust.delete()
