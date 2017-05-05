"""
Created by haldunanil on 5/1/2017 per issue #7.
"""
from django.conf import settings


class ProcessTransaction(object):

    def __init__(self, user, amount):
        """

        """
        self.user = user
        self.amount = amount

    def calculate_commission(self, variable_rate=0.05, fixed_rate=100,
                             pay_as_you_go=False, *args, **kwargs):
        """

        """
        if pay_as_you_go:
            return self.amount * variable_rate + fixed_rate

        return self.amount * variable_rate

    def calculate_stripe_fee(self, *args, **kwargs):
        """

        """
        return self.amount * settings.STRIPE_VAR_FEE_PERC + \
            settings.STRIPE_FIXED_FEE_DOLLAR

    def calculate_shared_revenue(self, variable_rate=0.05, fixed_rate=100,
                                 pay_as_you_go=False, *args, **kwargs):
        """

        """
        cash_only_commission = self.calculate_commission(
            self.amount, variable_rate, fixed_rate, pay_as_you_go,
            *args, **kwargs
        )

        stripe_fee = calculate_stripe_fee(self.amount + cash_only_commission)

        return cash_only_commission - stripe_fee

    def calculate_business_share(self, business,
                                 variable_rate=0.05, fixed_rate=100,
                                 pay_as_you_go=False, *args, **kwargs):
        """

        """
        shareable_revenue = self.calculate_shared_revenue(
            self.amount, variable_rate, fixed_rate, pay_as_you_go,
            *args, **kwargs
        )

        return shareable_revenue * business.rev_share_perc
