from django import forms
from django.forms import ModelForm
from django.forms.models import model_to_dict, fields_for_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Businesses

class RegistrationForm(UserCreationForm):
    username = forms.EmailField(required=True, max_length=150, label='Email')
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Password (Confirm)'

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['username']

        if commit:
            user.save()

        group = Group.objects.get(name='Consumers')
        group.user_set.add(user)

        return user


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number',)
        widgets = {
            'phone_number': forms.TextInput(
                attrs={
                    "type": "tel",
                    "placeholder": "Phone Number"
                }
            )
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Email'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

class BusinessForm(ModelForm):
    class Meta:
        model = Businesses
        exclude = (
            'country',
            'rev_share_perc',
            'stripe_id',
            'owner',
        )
