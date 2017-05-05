from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def not_loggedin_required(function):
    """
    Requires that user NOT be logged in
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/') # redirect to home page
        else:
            return function(request, *args, **kwargs)
    return wrap

def profile_does_not_exist(function):
    """
    Requires that user NOT have a profile associated
    """
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            return redirect('/') # redirect to home page
        else:
            return function(request, *args, **kwargs)
    return wrap
