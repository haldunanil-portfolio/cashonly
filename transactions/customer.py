"""
Created by haldunanil on 4/30/2017 per issue #7.
"""
import stripe
from django.contrib.auth.models import Group

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
