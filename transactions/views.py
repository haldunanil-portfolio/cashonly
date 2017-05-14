from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from transactions.forms import BillSelectForm
from transactions.models import Bill
from django.contrib import messages


@login_required(login_url='/sign-in/')
def select_bill(request):
    """
    Finds a bill based on its ID number.
    """
    if request.method == 'POST':
        form = BillSelectForm(request.POST)
        if form.is_valid():
            # look up db for id number
            bill = Bill.objects.get(id=form.cleaned_data['bill_code'])

            # bill has to be unpaid
            if not bill.paid:

                # if no customer associated, send user to confirmation page
                if bill.customer is None:
                    return render(request, 'bill_select.html', {'bill': bill,
                                                                'message': "No customer yet."})

                # if customer associated, send user to payment page
                elif bill.customer is not None and bill.customer == request.user:
                    return render(request, 'bill_select.html', {'bill': bill,
                                                                'message': "Customer already confirmed."})

                # if different customer associated, send back
                else:
                    messages.info(request, "This bill ain't yours.")
                    return redirect('/select-bill/')

            # if bill already paid, inform user and send back
            else:
                messages.info(request, "Bill already paid.")
                return redirect('/select-bill/')

    else:
        form = BillSelectForm()

    return render(request, 'bill_select.html', {'form': form})


@login_required(login_url='/sign-in/')
def view_bill(request):
    """
    Finds a bill based on its ID number.
    """
    pass
