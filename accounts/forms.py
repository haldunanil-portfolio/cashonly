from django import forms
from django.forms import ModelForm
from django.forms.models import model_to_dict, fields_for_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile

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



class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, label="Email")
