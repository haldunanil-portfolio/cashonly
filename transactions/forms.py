from django import forms
from django.forms import ModelForm
from django.utils import html
from transactions.models import Bill


# customer section

class BillSelectForm(forms.Form):
    bill_code = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "type": "tel",
                "placeholder": "Enter Bill Code Here"
                }
        )
    )


class SubmitButtonWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return '<button type="submit" name="%s" value="%s">' % (html.escape(name), html.escape(value))


class SubmitButtonField(forms.Field):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = SubmitButtonWidget

        super(SubmitButtonField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value

class CustomTipForm(forms.Form):
    tip_amount = forms.DecimalField(label='Tip Amount',
                                    decimal_places=2,
                                    widget=forms.NumberInput(
                                        attrs={
                                            "type": "number",
                                            "placeholder": "Custom Tip Amount"
                                        }
                                    ))


# business section

class CreateEditBillForm(forms.Form):
    human_amount = forms.DecimalField(label='Purchase Amount',
                                      decimal_places=2,
                                      widget=forms.NumberInput(
                                          attrs={
                                              "type": "number",
                                              "placeholder": "Enter Bill Amount"
                                          }
                                      ))
