from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from transactions.forms import BillSelectForm
from transactions.models import Bill
from django.contrib import messages
from django.http import Http404
from transactions.forms import TipForm
from transactions.forms import CustomTipForm
from django.core.exceptions import ObjectDoesNotExist


# customer section

@login_required(login_url='/sign-in/')
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
                    messages.info(request, "This bill ain't yours.")

            return redirect(url)

    else:
        form = BillSelectForm()

    return render(request, 'bill_select.html', {'form': form})


@login_required(login_url='/sign-in/')
def view_bill(request, bill_id):
    """
    Finds a bill based on its ID number.
    """
    try:
        bill = Bill.objects.get(id=bill_id)
    except ValueError:
        raise Http404()

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill ain't yours.")
        return redirect('/select-bill/')

    return render(
        request, 'bill_view.html',
        {
            'bill': bill,
            'confirm_url': '/select-bill/%s/confirm/' % bill.id
        }
    )


@login_required(login_url='/sign-in/')
def confirm_bill(request, bill_id):
    """
    Confirms a bill and associates it with a user
    """
    bill = Bill.objects.get(id=bill_id)

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed, then back to select bill
    elif bill.customer is not None:
        messages.info(request, "This bill ain't yours.")
        return redirect('/select-bill/')

    bill.customer = request.user
    bill.save()

    url = '/select-bill/%s/tip/' % bill.id

    return redirect(url)


@login_required(login_url='/sign-in/')
def tip_bill(request, bill_id):
    """
    Tip a bill
    """
    bill = Bill.objects.get(id=bill_id)

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill ain't yours.")
        return redirect('/select-bill/')

    if request.method == "POST":
        form = TipForm(request.POST)
        if form.is_valid():

            # determine if tip amount is custom or not
            if form.cleaned_data['tip_amount'] == 'custom':
                pass

            # if not custom, add amount to bill object and go to payment screen
            else:
                tip_amount = float(form.cleaned_data['tip_amount']) * bill.amount
                bill.tip = tip_amount
                bill.save()

                url = '/select-bill/%s/pay/' % bill.id
                return redirect(url)

    else:
        form = TipForm()

    return render(request, 'bill_pay.html', {'form': form, 'bill': bill})


@login_required(login_url='/sign-in/')
def pay_bill(request, bill_id):
    """
    Pay a bill

    ## Some Stripe shit will happen here
    ## IMPLEMENTATION NOT COMPLETE
    """
    bill = Bill.objects.get(id=bill_id)

    # if bill was alredy paid, then back to select bill
    if bill.paid:
        messages.info(request, "This bill has already been paid.")
        return redirect('/select-bill/')

    # if bill confirmed by another customer, then back to select bill
    elif bill.customer is not None and bill.customer != request.user:
        messages.info(request, "This bill ain't yours.")
        return redirect('/select-bill/')

    return render(request, 'bill_pay.html', {'bill': bill})


@login_required(login_url='/sign-in/')
def bill_success(request, bill_id):
    """
    Display success message when bill has been successfully paid.
    """
    bill = Bill.objects.get(id=bill_id)

    if bill.paid:
        return render(request, 'bill_success.html', {'bill': bill})
    else:
        url = '/select-bill/%s/tip/' % bill.id
        return redirect(url)


# business section

def create_bill(request):
    """
    Creates a new bill
    """
    pass
