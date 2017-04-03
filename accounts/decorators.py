from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def referer_matches_re(regex):
    """
    Decorator for views that checks that if the request's HTTP_REFERER matches
    the supplied regex pattern. Failure sends user back to homepage.
    """
    import re
    regex = re.compile(regex)
    def _dec(view_func):
        def _check_referer(request, *args, **kwargs):
            referer = request.META.get('HTTP_REFERER', '/')
            if regex.search(referer):
                return view_func(request, *args, **kwargs)
            return redirect('/')
        _check_referer.__doc__ = view_func.__doc__
        _check_referer.__dict__ = view_func.__dict__
        return _check_referer
    return _dec

def not_loggedin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('/') # redirect to home page
        else:
            return function(request, *args, **kwargs)
    return wrap
