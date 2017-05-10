from django.test import TestCase
from transactions.processing import SimpleTransaction
from transactions.processing import PayAsYouGo
from transactions.processing import AddToBalance
from transactions.processing import PurchaseFromBalance
from transactions.models import Bill
from transactions.models import Businesses
from transactions.models import Charge
from transactions.models import CustomerBalance


class SimpleTransactionInitTests(TestCase):

    def test_initialize_with_user_amount(self):
        """
        Valid SimpleTransaction instance should be created when supplied
        with both a user and an amount.
        """
        username, pw = 'test@example.com', 'test1234'
        user = User.objects.create_user(username, password=pw)
        user.save()

        result = SimpleTransaction(user=user, amount=1000)
        self.assertIsInstance(result, SimpleTransaction)

    def test_initialize_with_bill(self):
        """
        Valid SimpleTransaction instance should be created when supplied
        with a bill instance.
        """
        # create a business
        biz = Businesses.objects.create(
            name='Test, Inc.', address_1='123 Main Street', city='New York',
            state_province='NY', zipcode='10028', country='US'
        )
        biz.save()

        # create a bill and associate with the above business
        bill = Bill.objects.create(
            business=biz, amount=1000
        )
        bill.save()

        result = SimpleTransaction(bill=bill)
        self.assertIsInstance(result, SimpleTransaction)

    def test_initialize_incomplete1(self):
        """
        SimpleTransaction instance should raise an error when only supplied
        with a user instance (no amount or bill).
        """
        username, pw = 'test@example.com', 'test1234'
        user = User.objects.create_user(username, password=pw)
        user.save()

        with self.assertRaisesMessage(AssertionError, "Must supply user AND amount, or bill."):
            SimpleTransaction(user=user)

    def test_initialize_incomplete2(self):
        """
        SimpleTransaction instance should raise an error when only supplied
        with an amount value (no user or bill).
        """
        with self.assertRaisesMessage(AssertionError, "Must supply user AND amount, or bill."):
            SimpleTransaction(amount=1000)

    def test_initialization_with_var_fee(self):
        """

        """
        raise NotImplementedError

    def test_initialization_without_var_fee(self):
        """

        """
        raise NotImplementedError

    def test_initialization_with_fixed_fee(self):
        """

        """
        raise NotImplementedError

    def test_initialization_without_fixed_fee(self):
        """

        """
        raise NotImplementedError

    def test_initialization_with_pay_as_you_go_true(self):
        """

        """
        raise NotImplementedError

    def test_initialization_with_pay_as_you_go_false(self):
        """

        """
        raise NotImplementedError

    def test_initialization_without_pay_as_you_go(self):
        """

        """
        raise NotImplementedError

    def test_var_fee_float(self):
        """

        """
        raise NotImplementedError

    def test_var_fee_gt_0(self):
        """

        """
        raise NotImplementedError

    def test_var_fee_lt_1(self):
        """

        """
        raise NotImplementedError

    def test_fixed_fee_gt_0(self):
        """

        """
        raise NotImplementedError

    def test_pay_as_you_go_bool(self):
        """

        """
        raise NotImplementedError

    def test_business_isinstance_Business(self):
        """

        """
        raise NotImplementedError

class PayAsYouGoTests(TestCase):
    pass


class AddToBalanceTests(TestCase):
    pass


class PurchaseFromBalanceTests(TestCase):
    pass
