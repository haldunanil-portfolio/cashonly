"""
Created by haldunanil on 5/1/2017 per issue #7.
"""
from appconfig.functions import get_value


class SimpleTransaction(object):

    def __init__(self, user, amount, *args, **kwargs):
        """
        Optional inputs:
        - cash_only_var_fee = must be a decimal between 0 and 1
        - cash_only_fixed_fee = must be an amount expressed in cents
        - pay_as_you_go = True or False depending on whether the transaction
                          should have a pay-as-you-go surcharge
        """
        self.user = user
        self.amount = amount

        # get variable fee to charge
        if 'cash_only_var_fee' in kwargs:
            self.cash_only_var_fee = kwargs['cash_only_var_fee']
        else:
            self.cash_only_var_fee = get_value("CASH_ONLY_VAR_FEE")

        # get fixed fee to charge
        if 'cash_only_fixed_fee' in kwargs:
            self.cash_only_fixed_fee = kwargs['cash_only_fixed_fee']
        else:
            self.cash_only_fixed_fee = get_value("CASH_ONLY_FIXED_FEE")

        # determine whether transaction is a pay-as-you-go transactions
        if 'pay_as_you_go' in kwargs:
            self.pay_as_you_go = kwargs['pay_as_you_go']
        else:
            self.pay_as_you_go = False

    def __str__(self):
        return u'%s has a trx worth $%s' % (self.user, self.amount)

    def calculate_commission(self, *args, **kwargs):
        """
        Calculate the amount of commission to charge user.

        Returns: the commission amount to be charged
        """
        if self.pay_as_you_go:
            return self.amount * self.cash_only_var_fee + self.cash_only_fixed_fee

        return self.amount * self.cash_only_var_fee

    def calculate_stripe_fee(self, *args, **kwargs):
        """
        Calculate the amount of stripe fee expected to be charged.

        Returns: the fee charged by stripe
        """
        result = (self.amount + self.calculate_commission()) * \
            get_value("STRIPE_VAR_FEE_PERC") + \
            get_value("STRIPE_FIXED_FEE_DOLLAR")

        return round(result, 2)

    def calculate_shared_revenue(self, *args, **kwargs):
        """
        Calculate the amount of shareable commission revenue after stripe fees.

        Returns: the amount of total shared commission revenue
        """
        return round(self.calculate_commission() - self.calculate_stripe_fee(),2)

    def calculate_business_share(self, business, *args, **kwargs):
        """
        Calculate the amount of commission given to business after stripe fees.

        Inputs:
        - business = accounts.models.Businesses instance

        Returns: the amount commission revenue shared with business
        """
        return round(self.calculate_shared_revenue() *
                     float(business.rev_share_perc), 2)
