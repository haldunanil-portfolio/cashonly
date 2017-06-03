from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from transactions.forms import BillSelectForm
from transactions.models import Bill
from django.contrib import messages
from django.http import Http404
from transactions.forms import TipForm
from transactions.forms import CustomTipForm
from transactions.forms import RefillAccountForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test
from transactions.forms import CreateEditBillForm
from transactions.processing import AddToBalance
from transactions.processing import PurchaseFromBalance
from transactions.processing import PayAsYouGo
from django.db.models import Sum
import stripe


####################
# helper functions #
####################


####################
# customer section #
####################


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def see_cards(request):
    """
    See added credit cards
    """
    # get stripe object
    stripe.api_key = settings.STRIPE_API_TEST_SECRET
    stripe_cust = stripe.Customer.retrieve(request.user.profile.stripe_id)

    # check if default card set, if not return empty page
    if stripe_cust.default_source is None:
        return render(request, 'see_cards.html')

    # get list of payment methods
    methods = stripe_cust.sources.data
    default_id = stripe_cust.default_source

    return render(request, 'see_cards.html', {'methods': methods,
                                              'default_id': default_id})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def add_new_card(request):
    """
    Adds a new credit card to stripe
    """
    if request.method == "POST":
        # grab the stripe token
        stripe_token = request.POST.get("stripeToken")

        # create a stripe card element
        stripe.api_key = settings.STRIPE_API_TEST_SECRET
        stripe_cust = stripe.Customer.retrieve(request.user.profile.stripe_id)
        new_card = stripe_cust.sources.create(source=stripe_token)

        return render(request, 'add_card.html', {'new_card': new_card})

    # get stripe public key
    stripe_public_key = settings.STRIPE_API_TEST_PUBLIC

    return render(
        request, 'add_card.html', {'stripe_public_key': stripe_public_key}
    )


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def change_default_card(request):
    """
    Changes default credit card
    """
    if request.method == 'POST':
        # get stripe object
        stripe.api_key = settings.STRIPE_API_TEST_SECRET
        stripe_cust = stripe.Customer.retrieve(request.user.profile.stripe_id)

        # make updates
        stripe_cust.default_source = request.POST.get("new_default")
        stripe_cust.save()

        # inform user that change happened
        messages.info(request, "Default card successfully changed.")

    return redirect('/cards/')


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def reload_my_account(request):
    """
    Adds money to user balance
    """
    if request.method == 'POST':
        form = RefillAccountForm(request.POST)
        if form.is_valid():
            # grab the submitted amount
            amount = float(form.cleaned_data['amount'])

            # create an AddToBalance instance and process it
            added_balance = AddToBalance(user=request.user, amount=amount)

            # attempt to make the charge, catch error as message
            try:
                added_balance.process()
            except ValueError as e:
                messages.info(request, 'ERROR: %s' % e)
                return redirect('/cards/add/')

            # inform user that the submission was added successfully
            amount_dollars = amount / 100
            messages.info(
                request, "$%.2f was successfully added to your balance!" % amount_dollars
            )
            return redirect('/')

    else:
        form = RefillAccountForm()

    return render(request, 'add_to_balance.html', {'form': form})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def select_bill(request):
    """
    Finds a bill based on its ID number.
    """
    if request.method == 'POST':
        form = BillSelectForm(request.POST)
        if form.is_valid():
            # look up db for id number
            try:
                bill = Bill.objects.get(id=form.cleaned_data['bill_code'])
            except ObjectDoesNotExist:
                messages.info(request, "Could not find the bill. Please try again.")
                return redirect('/select-bill/')

            # if bill already paid, inform user and send back
            if bill.paid:
                url = '/select-bill/'
                messages.info(request, "This bill has already been paid.")

            # bill has to be unpaid
            else:
                # if no customer associated, send user to confirmation page
                if bill.customer is None:
                    url = '/select-bill/%s/' % bill.id

                # if customer associated, send user to payment page
                elif bill.customer is not None and bill.customer == request.user:
                    url = '/select-bill/%s/tip/' % bill.id

                # if different customer associated, send back
                elif bill.customer is not None and bill.customer != request.user:
                    url = '/select-bill/'
                    messages.info(request, "This bill belongs to another customer.")

            return redirect(url)

    else:
        form = BillSelectForm()

    return render(request, 'bill_select_cust.html', {'form': form})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def view_bill(request, bill_id):
    """
    Finds a bill based on its ID number.
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill belongs to another customer.")
        return redirect('/select-bill/')

    return render(
        request, 'bill_view_cust.html',
        {
            'bill': bill,
            'confirm_url': '/select-bill/%s/confirm/' % bill.id
        }
    )


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def confirm_bill(request, bill_id):
    """
    Confirms a bill and associates it with a user
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed, then back to select bill
    elif bill.customer is not None:
        messages.info(request, "This bill belongs to another customer.")
        return redirect('/select-bill/')

    bill.customer = request.user
    bill.save()

    url = '/select-bill/%s/tip/' % bill.id

    return redirect(url)


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def tip_bill(request, bill_id):
    """
    Tip a bill
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill belongs to another customer.")
        return redirect('/select-bill/')

    if request.method == "POST":
        form = TipForm(request.POST)
        if form.is_valid():

            # determine if tip amount is custom or not
            if form.cleaned_data['tip_amount'] == 'custom':
                url = '/select-bill/%s/custom-tip/' % bill.id
                return redirect(url)

            # if not custom, add amount to bill object and go to payment screen
            else:
                tip_amount = float(form.cleaned_data['tip_amount']) * bill.amount
                bill.tip = tip_amount
                bill.save()

                url = '/select-bill/%s/pay/' % bill.id
                return redirect(url)

    else:
        form = TipForm()

    return render(request, 'bill_tip_cust.html', {'form': form, 'bill': bill})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def custom_tip_bill(request, bill_id):
    """
    Custom tip for bill
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill belongs to another customer.")
        return redirect('/select-bill/')

    if request.method == "POST":
        form = CustomTipForm(request.POST)
        if form.is_valid():
            tip_amount = float(form.cleaned_data['tip_amount']) * 100
            bill.tip = tip_amount
            bill.save()

            url = '/select-bill/%s/pay/' % bill.id
            return redirect(url)

    else:
        form = CustomTipForm()

    return render(request, 'bill_tip_cust.html', {'form': form, 'bill': bill})



@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def pay_bill(request, bill_id):
    """
    Pay a bill
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill belongs to another customer.")
        return redirect('/select-bill/')

    return render(request, 'bill_pay_cust.html', {'bill': bill})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def bill_confirmation(request, bill_id):
    """
    Confirm payment amount
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    return render(request, 'bill_pay_confirmation_cust.html', {'bill': bill})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def process_payment(request, bill_id):
    """
    Process bill payment
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    # charge amount and tip
    charge = bill.amount + bill.tip

    # charge to account, pay as you go otherwise
    if request.user.customerbalance.is_current_balance_sufficient(charge):
        purchase = PurchaseFromBalance(bill=bill)

    else:
        purchase = PayAsYouGo(bill=bill)

    # process the purchase
    purchase.process()

    url = '/select-bill/%s/success/' % bill.id
    return redirect(url)


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Consumers').exists())
def bill_success(request, bill_id):
    """
    Display success message when bill has been successfully paid.
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/select-bill/')

    if bill.paid:
        return render(request, 'bill_success_cust.html', {'bill': bill})

    else:
        url = '/select-bill/%s/' % bill.id
        return redirect(url)


####################
# business section #
####################

@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Business Employees').exists())
def create_bill(request):
    """
    Creates a new bill
    """
    if request.method == "POST":
        form = CreateEditBillForm(request.POST)
        if form.is_valid():
            bill = Bill.objects.create(
                business=request.user.profile.business,
                amount=form.cleaned_data['human_amount'] * 100
            )
            bill.save()
            url = '/bill/%s/checkout/' % bill.id
            return redirect(url)

    else:
        form = CreateEditBillForm()

    return render(request, 'bill_edit_biz.html', {'form': form})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Business Employees').exists())
def see_bill(request, bill_id):
    """
    Displays a bill
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/')

    # check if bill has already been paid, not ok otherwise
    if bill.paid:
        url = '/bill/%s/success/' % bill.id
        return redirect()

    # check if bill belongs to another business
    elif bill.business != request.user.profile.business:
        messages.info(request, "This bill was opened by another business.")
        return redirect('/')

    return render(request, 'bill_view_biz.html', {'bill': bill})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Business Employees').exists())
def edit_bill(request, bill_id):
    """
    Edits an existing bill
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/')

    # check if bill has already been paid, not ok otherwise
    if bill.paid:
        url = '/bill/%s/success/' % bill.id
        return redirect()

    # check if bill belongs to another business
    elif bill.business != request.user.profile.business:
        messages.info(request, "This bill was opened by another business.")
        return redirect('/')

    if request.method == "POST":
        form = CreateEditBillForm(request.POST)
        if form.is_valid():
            bill.amount = form.cleaned_data['human_amount'] * 100
            bill.save()
            return redirect('/bill/%s/checkout/' % bill.id)

    else:
        form = CreateEditBillForm()

    return render(request, 'bill_edit_biz.html', {'bill': bill, 'form': form})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Business Employees').exists())
def delete_bill(request, bill_id):
    """
    Deletes a bill
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/')

    # check if bill has already been paid, not ok otherwise
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/')

    # check if bill belongs to another business
    elif bill.business != request.user.profile.business:
        messages.info(request, "This bill was opened by another business.")
        return redirect('/')

    # delete bill if conditions passed
    bill.delete()

    return redirect('/')


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Business Employees').exists())
def bill_paid(request, bill_id):
    """
    Displays a success message indicating bill has been paid
    """
    # attempt to find the bill, otherwise send user back to bill selection
    try:
        bill = Bill.objects.get(id=bill_id)
    except ObjectDoesNotExist:
        messages.info(request, "A bill with this code does not exist.")
        return redirect('/')

    # check if bill has not yet been paid, not ok otherwise
    if not bill.paid:
        messages.info(request, "This bill has not yet been paid.")
        return redirect('/bill/%s/' % bill.id)

    # check if bill belongs to another business
    elif bill.business != request.user.profile.business:
        messages.info(request, "This bill was opened by another business.")
        return redirect('/')

    return render(request, 'bill_success_biz.html', {'bill': bill})


@login_required(login_url='/sign-in/')
@user_passes_test(lambda u: u.groups.filter(name='Business Employees').exists())
def transactions_biz(request):
    """
    Completed business transactions
    """
    bills = Bill.objects.filter(
        business=request.user.profile.business, paid=True
    )

    total = bills.aggregate(Sum('amount'))['amount__sum']

    return render(request, 'transactions_biz.html', {'bills': bills,
                                                     'total': total})
