from django import forms
from django.forms import ModelForm
from transactions.models import Bill


class BillSelectForm(forms.Form):
    bill_code = forms.IntegerField()
