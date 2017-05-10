from django.test import TestCase
from django.contrib.auth.models import User
from transactions.processing import SimpleTransaction
from transactions.processing import PayAsYouGo
from transactions.processing import AddToBalance
from transactions.processing import PurchaseFromBalance
from transactions.models import Bill
from transactions.models import Businesses
from transactions.models import Charge
from transactions.models import CustomerBalance
from appconfig.models import Config
from random import random


class SimpleTransactionInitTests(TestCase):

    def setUp(self):
        # create a user
        username = 'test%s@example.com' % int(random() * 10000)
        pw = 'test1234'
        self.user = User.objects.create_user(username, password=pw)
        self.user.save()

        # create a business
        self.biz = Businesses.objects.create(
            name='Test, Inc.', address_1='123 Main Street', city='New York',
            state_province='NY', zipcode='10028', country='US'
        )
        self.biz.save()

        # create a self.bill and associate with the above business
        self.bill = Bill.objects.create(
            business=self.biz, amount=1000
        )
        self.bill.save()

        # create the requisite configs
        config1 = Config.objects.create(
            key="CASH_ONLY_VAR_FEE",
            value=0.05
        )
        config1.save()

        config2 = Config.objects.create(
            key="CASH_ONLY_FIXED_FEE",
            value=1
        )
        config2.save()

    def test_initialize_with_user_amount(self):
        """
        Valid SimpleTransaction instance should be created when supplied
        with both a user and an amount.
        """
        result = SimpleTransaction(user=self.user, amount=1000)
        self.assertIsInstance(result, SimpleTransaction)

    def test_initialize_with_bill(self):
        """
        Valid SimpleTransaction instance should be created when supplied
        with a self.bill instance.
        """
        result = SimpleTransaction(bill=self.bill)
        self.assertIsInstance(result, SimpleTransaction)

    def test_initialize_incomplete1(self):
        """
        SimpleTransaction instance should raise an error when only supplied
        with a user instance (no amount or self.bill).
        """
        username, pw = 'test@example.com', 'test1234'
        user = User.objects.create_user(username, password=pw)
        user.save()

        with self.assertRaisesMessage(AssertionError, "Must supply user AND amount, or bill."):
            SimpleTransaction(user=user)

    def test_initialize_incomplete2(self):
        """
        SimpleTransaction instance should raise an error when only supplied
        with an amount value (no user or self.bill).
        """
        with self.assertRaisesMessage(AssertionError, "Must supply user AND amount, or bill."):
            SimpleTransaction(amount=1000)

    def test_initialization_with_var_fee(self):
        """
        Test to see whether a variable cash only fee is correctly added to
        a SimpleTransaction instance.
        """
        result = SimpleTransaction(bill=self.bill, cash_only_var_fee=0.10)
        self.assertEqual(result.cash_only_var_fee, 0.10)

    def test_initialization_without_var_fee(self):
        """
        Test to see whether a variable cash only fee is correctly grabbed
        from app config when no value supplied to the class.
        """
        result = SimpleTransaction(bill=self.bill)
        self.assertEqual(result.cash_only_var_fee, 0.05)

    def test_initialization_with_fixed_fee(self):
        """
        Test to see whether a fixed cash only fee is correctly added to
        a SimpleTransaction instance.
        """
        result = SimpleTransaction(bill=self.bill, cash_only_fixed_fee=1.5)
        self.assertEqual(result.cash_only_fixed_fee, 1.5)

    def test_initialization_without_fixed_fee(self):
        """
        Test to see whether a fixed cash only fee is correctly grabbed
        from app config when no value supplied to the class.
        """
        result = SimpleTransaction(bill=self.bill)
        self.assertEqual(result.cash_only_fixed_fee, 1)

    def test_initialization_with_pay_as_you_go_true(self):
        """
        Tests whether pay as you go is correctly initialized as True when
        value is provided.
        """
        result = SimpleTransaction(bill=self.bill, pay_as_you_go=True)
        self.assertEqual(result.pay_as_you_go, True)

    def test_initialization_with_pay_as_you_go_false(self):
        """
        Tests whether pay as you go is correctly initialized as False when
        value is provided.
        """
        result = SimpleTransaction(bill=self.bill, pay_as_you_go=False)
        self.assertEqual(result.pay_as_you_go, False)

    def test_initialization_without_pay_as_you_go(self):
        """
        Tests whether pay as you go is correctly initialized as False when
        value is not provided.
        """
        result = SimpleTransaction(bill=self.bill)
        self.assertEqual(result.pay_as_you_go, False)

    def test_var_fee_gt_0(self):
        """
        Tests if the value of the variable fee is greater than 0.
        """
        # try with a value gt 0, should be fine
        result1 = SimpleTransaction(bill=self.bill, cash_only_var_fee=0.5)
        self.assertIsInstance(result1, SimpleTransaction)

        # try with a value lt 0, should raise an error
        with self.assertRaisesMessage(AssertionError, "cash_only_var_fee must be > 0.0"):
            result2 = SimpleTransaction(bill=self.bill, cash_only_var_fee=-0.5)

    def test_var_fee_lt_1(self):
        """
        Tests if the value of the variable fee is less than 1.
        """
        # try with a value gt 0, should be fine
        result1 = SimpleTransaction(bill=self.bill, cash_only_var_fee=0.5)
        self.assertIsInstance(result1, SimpleTransaction)

        # try with a value lt 0, should raise an error
        with self.assertRaisesMessage(AssertionError, "cash_only_var_fee must be <= 1.0"):
            result2 = SimpleTransaction(bill=self.bill, cash_only_var_fee=1.5)

    def test_fixed_fee_gt_0(self):
        """
        Tests if the value of the fixed fee is greater than 0.
        """
        # try with a value gt 0, should be fine
        result1 = SimpleTransaction(bill=self.bill, cash_only_fixed_fee=0.5)
        self.assertIsInstance(result1, SimpleTransaction)

        # try with a value lt 0, should raise an error
        with self.assertRaisesMessage(AssertionError, "cash_only_fixed_fee must be > 0.0"):
            result2 = SimpleTransaction(bill=self.bill, cash_only_fixed_fee=-0.5)

    def test_pay_as_you_go_bool(self):
        """
        Tests if the value of the fixed fee returns an error when not a boolean.
        """
        # try with a string, should raise an error
        with self.assertRaisesMessage(AssertionError, "pay_as_you_go must be boolean"):
            result = SimpleTransaction(bill=self.bill, pay_as_you_go='bool')

        # try with an int, should raise an error
        with self.assertRaisesMessage(AssertionError, "pay_as_you_go must be boolean"):
            result = SimpleTransaction(bill=self.bill, pay_as_you_go=1)

        # try with a float, should raise an error
        with self.assertRaisesMessage(AssertionError, "pay_as_you_go must be boolean"):
            result = SimpleTransaction(bill=self.bill, pay_as_you_go=1.0)

        # try with a list, should raise an error
        with self.assertRaisesMessage(AssertionError, "pay_as_you_go must be boolean"):
            result = SimpleTransaction(bill=self.bill, pay_as_you_go=[True, False])

        # try with a dict, should raise an error
        with self.assertRaisesMessage(AssertionError, "pay_as_you_go must be boolean"):
            result = SimpleTransaction(bill=self.bill, pay_as_you_go={'key':True})

    def test_business_isinstance_Business(self):
        """
        Tests if the business is a true instance of a business.
        """
        # try feeding it an actual business instance
        result0 = SimpleTransaction(bill=self.bill, business=self.biz)
        self.assertIsInstance(result0, SimpleTransaction)

        # try feeding it a wrong instance
        with self.assertRaisesMessage(AssertionError, "business must be an accounts.models.Businesses object"):
            result1 = SimpleTransaction(bill=self.bill, business='self.biz')

    

# class PayAsYouGoTests(TestCase):
#     pass
#
#
# class AddToBalanceTests(TestCase):
#     pass
#
#
# class PurchaseFromBalanceTests(TestCase):
#     pass
