from django import forms
from django.forms import ModelForm
from django.utils import html
from transactions.models import Bill


class BillSelectForm(forms.Form):
    bill_code = forms.IntegerField()


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
                   'class': 'button'}
        ),
        choices=OPTIONS
    )


class CustomTipForm(forms.Form):
    tip_amount = forms.DecimalField()
