"""cashonly URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login
from cashonly.views import home
from accounts.views import registration, registration_next_steps, signout
from accounts.forms import LoginForm
from django.views.generic import TemplateView
from cashonly.views import handler404 #### remove after testing

urlpatterns = [
    url(r'^$', home),
    url(r'^admin/', admin.site.urls),
    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt",
                                              content_type="text/plain"),
                                              name="robots_file"),
    url(r'^sign-up/$', registration, name='registration'),
    url(r'^sign-in/$', login, {
        'template_name': 'auth_form.html',
        'authentication_form': LoginForm
    }, name='login'),
    url(r'^sign-out/$', signout, name='signout'),
    url(r'^sign-up/more-details/$', registration_next_steps,
        name='registration_next_steps'),
    url(r'^404/$', handler404), #### remove after testing
]
