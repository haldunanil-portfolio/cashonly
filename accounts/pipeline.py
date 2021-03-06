from django.contrib.auth.models import Group
from accounts.forms import ProfileForm
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import urllib

# This is initially from https://github.com/python-social-auth/social-core/blob/master/social_core/pipeline/user.py
def get_username(strategy, details, backend, user=None, *args, **kwargs):
    """
    Ensures that username is user's email
    """
    # Get the logged in user (if any)
    logged_in_user = strategy.storage.user.get_username(user)

    # Custom: check for email being provided
    if not details.get('email'):
        error = "Sorry, but %s needs to provide us your email address." % backend.name.title()
        raise AssertionError(error)

    # Custom: if user is already logged in, double check his email matches the social network email
    if logged_in_user:
        if logged_in_user.lower() != details.get('email').lower():
            error = "Sorry, but you are already logged in with another account, and the email addresses do not match. Try logging out first, please."
            raise AssertionError(error)

    return {
        'username': details.get('email').lower(),
    }

def add_to_group(strategy, details, backend, user=None, *args, **kwargs):
    """
    Checks if user belongs to any groups. If not, adds user to 'Consumers'
    group.
    """
    if backend.name == 'facebook' or backend.name == 'google-oauth2':
        groups_list = user.groups.values_list('name',flat=True)
        if len(groups_list) == 0:
            # add this to the consumer group
            g = Group.objects.get(name='Consumers')
            g.user_set.add(user)
