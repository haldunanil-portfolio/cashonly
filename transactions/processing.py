"""
Created by haldunanil on 5/1/2017 per issue #7.
"""
from appconfig.functions import get_value
from django.conf import settings
from django.contrib.auth.models import Group
from accounts.models import Businesses
from transactions.models import CustomerBalance
from transactions.models import Bill
from transactions.models import Charge
import stripe


class SimpleTransaction(object):

    def __init__(self, *args, **kwargs):
        """
        Kwargs MUST either contain user AND amount OR a Bill instance.

        A Bill instance is the preferred approach, as it contains a more
        complete set of data and facilitates association. Indeed, a Bill
        instance MUST be supplied when the transaction is PayAsYouGo type.

        Required inputs:
        - user = User instance from django.contrib.auth.models
        - amount = integer
        OR
        - bill = Bill instance from transactions.models

        Optional inputs:
        - cash_only_var_fee = must be a decimal between 0 and 1
        - cash_only_fixed_fee = must be an amount expressed in cents
        - pay_as_you_go = True or False depending on whether the transaction
                          should have a pay-as-you-go surcharge
        - business = accounts.models.Businesses instance
        """
        # initialize user and amount
        if 'bill' in kwargs:
            self.bill = kwargs['bill']
            self.user = kwargs['bill'].customer
            self.amount = kwargs['bill'].amount
            self.business = kwargs['bill'].business

        elif 'user' in kwargs and 'amount' in kwargs:
            self.user = kwargs['user']
            self.amount = kwargs['amount']

        else:
            raise AssertionError("Must supply user AND amount, or bill.")

        # get variable fee to charge
        try:
            # check that the value is a value between [0, 1]
            assert kwargs['cash_only_var_fee'] <= 1.0, "cash_only_var_fee must be <= 1.0; you provided %s" % kwargs['cash_only_var_fee']
            assert kwargs['cash_only_var_fee'] > 0.0, "cash_only_var_fee must be > 0.0; you provided %s" % kwargs['cash_only_var_fee']

            # if checks passed, assign value
            self.cash_only_var_fee = kwargs['cash_only_var_fee']
        except KeyError:
            self.cash_only_var_fee = get_value("CASH_ONLY_VAR_FEE")

        # get fixed fee to charge
        try:
            # check that value is a positive integer or float
            assert kwargs['cash_only_fixed_fee'] > 0.0, "cash_only_fixed_fee must be > 0.0; you provided %s" % kwargs['cash_only_fixed_fee']

            # if checks passed, assign value
            self.cash_only_fixed_fee = kwargs['cash_only_fixed_fee']
        except KeyError:
            self.cash_only_fixed_fee = get_value("CASH_ONLY_FIXED_FEE")

        # determine whether transaction is a pay-as-you-go transactions
        try:
            # check that value is a boolean
            assert type(kwargs['pay_as_you_go']) == bool, "pay_as_you_go must be boolean; you provided %s" % kwargs['pay_as_you_go']

            # if checks passed, assign value
            self.pay_as_you_go = kwargs['pay_as_you_go']
        except KeyError:
            self.pay_as_you_go = False

        # set business if provided in kwargs
        try:
            # check that param is a accounts.models.Business instance
            assert isinstance(kwargs['business'], Businesses), "business must be an accounts.models.Businesses object; you provided %s" % type(kwargs['business'])

            #if checks passed, assign value
            self.business = kwargs['business']
        except KeyError:
            print("CAUTION: No business provided.")

    def __str__(self):
        return u'%s has a trx worth $%s' % (self.user, self.amount / 100)

    def _calculate_commission(self, *args, **kwargs):
        """
        Calculate the amount of commission to charge user.

        Returns: the commission amount to be charged
        """
        if self.pay_as_you_go:
            return self.amount * self.cash_only_var_fee + self.cash_only_fixed_fee

        return int(self.amount * self.cash_only_var_fee)

    def _calculate_stripe_fee(self, *args, **kwargs):
        """
        Calculate the amount of stripe fee expected to be charged.

        Returns: the fee charged by stripe
        """
        result = (self.amount + self._calculate_commission()) * \
            get_value("STRIPE_VAR_FEE_PERC") + \
            get_value("STRIPE_FIXED_FEE_DOLLAR")

        return int(round(result))

    def _calculate_shared_revenue(self, *args, **kwargs):
        """
        Calculate the amount of shareable commission revenue after stripe fees.

        Returns: the amount of total shared commission revenue
        """
        return int(round(
            self._calculate_commission() - self._calculate_stripe_fee(), 0
        ))

    def _calculate_business_share(self, *args, **kwargs):
        """
        Calculate the amount of commission given to business after stripe fees.

        Returns: the amount commission revenue shared with business
        """
        if 'business' in kwargs:
            return int(round(
                self._calculate_shared_revenue() *
                float(self.business.rev_share_perc), 0
            ))
        else:
            return int(round(
                self._calculate_shared_revenue() *
                get_value("DEFAULT_REV_SHARE"), 0
            ))

    def _create_stripe_charge(self, source, comments=None, *args, **kwargs):
        """
        Creates a stripe charge for the user.

        Inputs:
        - source = token to be used for the transaction
        - comments = Optional; any comments to be included with the charge.

        Returns: result of a stripe.Charge.create API call
        """
        # create an internal charge object
        internal_charge = Charge.objects.create(
            customer=self.user,
            amount=self.amount + self._calculate_commission(),
            commission=self._calculate_shared_revenue() - self._calculate_business_share(),
            stripe_fee=self._calculate_stripe_fee(),
            comments=comments
        )
        internal_charge.save()

        # give stripe our API key
        stripe.api_key = settings.STRIPE_API_SECRET

        # initialize common charge info
        basic_info = {
            "amount": int(self.amount + self._calculate_commission()),
            "currency": "usd",
            "source": source,
            "customer": self.user.profile.stripe_id,
            "description": comments
        }

        # if direct payment to business (assuming it exists)
        if self.pay_as_you_go:
            basic_info['destination'] = {
                "amount": int(self.amount + self._calculate_business_share()),
                "account": self.business.stripe_id
            }

            # it's a pay-as-you-go charge, so associate the bill immediately
            self.bill.charge = internal_charge
            self.bill.save()

        # else must contain a transfer group and add to customer balance
        else:
            basic_info['transfer_group'] = internal_charge.id

        # attempt to create the stripe charge, catch errors in the view
        stripe_charge = stripe.Charge.create(**basic_info)

        # assuming the charge above didn't fail, record info in db
        internal_charge.stripe_id = stripe_charge.id
        internal_charge.fail = False
        internal_charge.save()

        return stripe_charge

    def _create_stripe_transfer(self, comments=None, *args, **kwargs):
        """
        Makes a transfer from a user's account to a business.

        NOTE: Business must be specified, otherwise will return AssertionError.

        Inputs:
        - comments = Optional; any comments to be included with the charge.
        """
        # check to see if business is specified
        assert hasattr(self, 'business'), "Must specify a business."
        assert hasattr(self, 'bill'), "Must specify a bill."

        # check if amount is enough; if not, raise error
        if not self.user.customerbalance.is_current_balance_sufficient(
            self.amount
        ):
            raise ValueError("Insufficient balance.")

        # give stripe our API key
        stripe.api_key = settings.STRIPE_API_SECRET

        # get most recent charge element
        recent_charge = Charge.objects.filter(customer=self.user).latest()

        # create transfer on stripe, catch errors in the view
        stripe_transfer = stripe.Transfer.create(
            amount=self.amount + self._calculate_business_share(),
            currency="usd",
            transfer_group=recent_charge.id,
            destination=self.business.stripe_id
        )

        # associate bill with charge
        self.bill.charge = recent_charge
        self.bill.save()

        print(self.bill)

        return stripe_transfer

    def process(self):
        """
        To be implemented in a child class.
        """
        raise NotImplementedError


class PayAsYouGo(SimpleTransaction):

    def __init__(self, *args, **kwargs):
        # set pay as you go as True
        kwargs['pay_as_you_go'] = True
        super().__init__(*args, **kwargs)
        if 'business' not in self.__dict__:
            raise AssertionError("Must specify a business.")
        if 'bill' not in self.__dict__:
            raise AssertionError("Must contain a bill instance.")
        if not self.pay_as_you_go:
            raise AssertionError("Must indicate transaction as pay-as-you-go.")

    def process(self, source, comments=None, *args, **kwargs):
        """
        Make a purchase directly.

        Inputs:
        - source = token to be used for the transaction
        - comments = Optional; any comments to be included with the charge.

        Return:
        - stripe.Charge.create response element
        """
        # Step 1: Try to make stripe charge; if declined, raise error
        charge = self._create_stripe_charge(source, comments=None)

        # Step 2: Mark bill as paid
        self.bill.paid = True
        self.bill.save()

        # Step 3: Return charge instance
        return charge


class AddToBalance(SimpleTransaction):

    def process(self, source, comments=None, *args, **kwargs):
        """
        Add to the user balance without making a purchase.

        Inputs:
        - source = token to be used for the transaction
        - comments = Optional; any comments to be included with the charge.

        Returns:
        - stripe.Charge.create response element
        """
        # Step 1: Try to make a stripe charge; catch errors in the view
        charge = self._create_stripe_charge(source, comments=None)

        # Step 2: Add to customer's balance
        self.user.customerbalance.add_to_customer_balance(self.amount)
        self.user.customerbalance.save()

        # Step 3 return status code
        return charge


class PurchaseFromBalance(SimpleTransaction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'business' not in self.__dict__:
            raise AssertionError("Must specify a business.")
        if 'bill' not in self.__dict__:
            raise AssertionError("Must contain a bill instance.")

    def process(self, comments=None, *args, **kwargs):
        """
        Make a purchase from existing balance.

        Inputs:
        - source = token to be used for the transaction
        - comments = Optional; any comments to be included with the charge.

        Returns:
        - stripe.Transfer.create response element
        """
        # Step 1: Check if amount is enough; if not, raise error
        if not self.user.customerbalance.is_current_balance_sufficient(
            self.amount
        ):
            raise ValueError("Insufficient balance.")

        # Step 2: Make a transfer to business' stripe account
        transfer = self._create_stripe_transfer(comments)

        # Step 3: Reduce customer balance
        self.user.customerbalance.reduce_customer_balance(self.amount)
        self.user.customerbalance.save()

        # Step 4: Mark bill as paid
        self.bill.paid = True
        self.bill.save()

        # Step 5: Return transfer charge instance
        return transfer






##### FOR TESTING PURPOSES, DELETE AFTERWARDS
# from django.contrib.auth.models import User
# from accounts.models import Businesses
#
# user = User.objects.get(username="haldunanil")
# biz = Businesses.objects.get(name="Test")
# bill1 = Bill.objects.get(id=8)
# bill2 = Bill.objects.get(id=9)
# a = SimpleTransaction(user=user, amount=3000, bill=bill)
# b = SimpleTransaction(user=user, amount=3000, business=biz, bill=bill, pay_as_you_go=True)
# x0 = a._create_stripe_charge(source='card_1AHOmRCX7PkkAZyTdl0Pdz2C')
# x1 = b._create_stripe_charge(source='card_1AHOmRCX7PkkAZyTdl0Pdz2C')
# y0 = a._create_stripe_transfer()
# y1 = b._create_stripe_transfer()

# a = AddToBalance(user=user, amount=5000)
# a.process(source='card_1AHOmRCX7PkkAZyTdl0Pdz2C')
# b = PurchaseFromBalance(bill=bill1)
# b.process()
# c = PurchaseFromBalance(bill=bill2)
# try:
#     c.process()
# except Exception as e:
#     print(e)
# d = PayAsYouGo(bill=bill2)
# d.process(source='card_1AHOmRCX7PkkAZyTdl0Pdz2C')

#####
