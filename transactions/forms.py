from django import forms
from django.forms import ModelForm
from django.utils import html
from transactions.models import Bill


# customer section

class RefillAccountForm(forms.Form):
    OPTIONS = (
        (2500, "$25 (+$1.25 fee)"),
        (5000, "$50 (+$2.5 fee)"),
        (10000, "$100 (+$5 fee)")
    )

    amount = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={'onclick': 'this.form.submit();',
                   'class': 'button'}
        ),
        choices=OPTIONS
    )

class BillSelectForm(forms.Form):
    bill_code = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "type": "tel"
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


class TipForm(forms.Form):
    OPTIONS = (
        (0.15, "15% Tip"),
        (0.18, "18% Tip"),
        (0.20, "20% Tip"),
        ("custom", "Custom")
    )

    tip_amount = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={'onclick': 'this.form.submit();',
                   'class': 'tip-radio'}
        ),
        choices=OPTIONS
    )


class CustomTipForm(forms.Form):
    tip_amount = forms.DecimalField(label='Tip Amount',
                                    decimal_places=2,
                                    widget=forms.NumberInput(
                                        attrs={
                                            "type": "number"
                                        }
                                    ))


# business section

class CreateEditBillForm(forms.Form):
    human_amount = forms.DecimalField(label='Purchase Amount',
                                      decimal_places=2,
                                      widget=forms.NumberInput(
                                          attrs={
                                              "type": "number"
                                          }
                                      ))
