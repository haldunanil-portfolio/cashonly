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
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login
from cashonly.views import home
from accounts.views import registration
from accounts.views import registration_next_steps
from accounts.views import signout
from accounts.views import business_sign_up
from accounts.forms import LoginForm
from accounts.forms import BusinessForm
from django.views.generic import TemplateView
from cashonly.views import handler404 #### remove after testing
from accounts.decorators import not_loggedin_required
from transactions.views import see_cards
from transactions.views import add_new_card
from transactions.views import change_default_card
from transactions.views import reload_my_account
from transactions.views import select_bill
from transactions.views import view_bill
from transactions.views import confirm_bill
from transactions.views import tip_bill
from transactions.views import pay_bill
from transactions.views import bill_success
from transactions.views import create_bill
from transactions.views import see_bill
from transactions.views import edit_bill
from transactions.views import delete_bill
from transactions.views import bill_paid

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt",
                                              content_type="text/plain"),
                                              name="robots_file"),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^sign-up/$', not_loggedin_required(registration), name='sign-up'),
    url(r'^sign-in/$', not_loggedin_required(login), {
        'template_name': 'auth_form.html',
        'authentication_form': LoginForm
    }, name='sign-in'),
    url(r'^sign-out/$', signout, name='sign-out'),
    url(r'^sign-up/more-details/$', registration_next_steps,
        name='registration_next_steps'),
    url(r'^404/$', handler404), #### remove after testing
    url(r'^business-sign-up/$', business_sign_up, name='business_sign_up'),
    url(r'^select-bill/$', select_bill, name='select_bill'),
    url(r'^select-bill/(\d+)/$', view_bill, name='view_bill'),
    url(r'^select-bill/(\d+)/confirm/$', confirm_bill, name='confirm_bill'),
    url(r'^select-bill/(\d+)/tip/$', tip_bill, name='tip_bill'),
    url(r'^select-bill/(\d+)/pay/$', pay_bill, name='pay_bill'),
    url(r'^select-bill/(\d+)/success/$', bill_success, name='bill_success'),
    url(r'^reload-my-account/$', reload_my_account, name="reload_my_account"),
    url(r'^create-bill/$', create_bill, name='create_bill'),
    url(r'^cards/$', see_cards, name='see_cards'),
    url(r'^cards/add/$', add_new_card, name='add_new_cards'),
    url(r'^cards/change-default/$', change_default_card, name='change_default'),
    url(r'^bill/(\d+)/$', see_bill, name='see_bill'),
    url(r'^bill/(\d+)/edit/$', edit_bill, name='edit_bill'),
    url(r'^bill/(\d+)/checkout/$', see_bill, name='checkout_bill'),
    url(r'^bill/(\d+)/delete/$', delete_bill, name='delete_bill'),
    url(r'^bill/(\d+)/success/$', bill_paid, name='bill_paid'),
    url(r'^tinymce/', include('tinymce.urls')),
]
