from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from accounts.forms import RegistrationForm
from accounts.forms import ProfileForm
from accounts.forms import BusinessForm
from accounts.models import BusinessType
from accounts.decorators import not_loggedin_required
from accounts.decorators import profile_does_not_exist
from django.contrib import messages
from accounts.stripe import create_managed_stripe_account
from accounts.stripe import create_customer_stripe_account
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from transactions.models import CustomerBalance
from django.http import JsonResponse
from accounts.models import Businesses
import time
import stripe


@not_loggedin_required
def registration(request):
	"""
	Registration method
	"""
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			# register user
			form.save()
			new_user = authenticate(username=form.cleaned_data['username'],
									password=form.cleaned_data['password1'])

			# send account creation confirmation email
			subject = "Thanks for signing up, %s!" % new_user.first_name
			from_email = 'info@cashon.ly'
			to = new_user.email

			html_content = render_to_string(
				'email_welcome.html', {'user': new_user}
			)
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
			msg.attach_alternative(html_content, "text/html")
			msg.send()

			# log user in
			login(request, new_user)
			return redirect('/sign-up/more-details/')

	else:
		form = RegistrationForm()

	return render(request, 'auth_form.html', {'form': form})


@profile_does_not_exist
@login_required(login_url='/sign-in/')
def registration_next_steps(request):
	"""
	Loads next steps page to complete user registration
	"""
	referer = request.META.get('data[HTTP_REFERER]', '')
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			# associate profile with user object
			next_step = form.save(commit=False)
			next_step.user = request.user

			# create a Stripe customer instance
			customer = create_customer_stripe_account(
				request.user, commit=False
			)
			next_step.stripe_id = customer.id

			# create a customer balance object of 0
			cbal = CustomerBalance.objects.create(customer=request.user)
			cbal.save()

			# save and redirect to home page
			next_step.save()
			return redirect('/')

	else:
		form = ProfileForm()

	return render(request, 'form-next-step.html', {'form': form})


def signout(request):
	"""
	Sign out method
	"""
	logout(request)
	return redirect('/')


@login_required(login_url='/sign-in/')
def business_sign_up(request):
	"""
	Sign up form for businesses
	"""
	business = request.user.profile.business

	if business:
		# get stripe account details
		stripe.api_key = settings.STRIPE_API_SECRET
		account = stripe.Account.retrieve(business.stripe_id)

		if len(account.verification.fields_needed) == 0:
			messages.info(request, 'You are already signed up to use Cash Only as a business.')
			return redirect('/')

	return render(request, 'business-sign-up.html', {
		'business_types': BusinessType.objects.all()
	})


## AJAX VIEWS

@login_required(login_url='/sign-in/')
def ajax_business_sign_up(request):
	"""
	Business sign up ajax request
	"""
	user = User.objects.get(
		username=request.POST.get('user', None)
	)

	if user is None:
		data = {'found_user': False}
		return JsonResponse(data)

	profile = user.profile

	# update existing business details
	if profile.business:
		business = profile.business
		business.name = request.POST.get('data[name]')
		business.website = request.POST.get('data[website]', None)
		business.yelp_page = request.POST.get('data[yelp_page]', None)
		business.facebook_page = request.POST.get('data[facebook_page]', None)
		business.address_1 = request.POST.get('data[address_1]')
		business.address_2 = request.POST.get('data[address_2]', None)
		business.city = request.POST.get('data[city]')
		business.state_province = request.POST.get('data[state_province]')
		business.zipcode = request.POST.get('data[zipcode]')
		business.save()

		# get stripe account details
		stripe.api_key = settings.STRIPE_API_SECRET
		account = stripe.Account.retrieve(business.stripe_id)

	# create new business
	else:
		# create business and associate user
		business = Businesses(
			name=request.POST.get('data[name]'),
			website=request.POST.get('data[website]', None),
			yelp_page=request.POST.get('data[yelp_page]', None),
			facebook_page=request.POST.get('data[facebook_page]', None),
			address_1=request.POST.get('data[address_1]'),
			address_2=request.POST.get('data[address_2]', None),
			city=request.POST.get('data[city]'),
			state=request.POST.get('data[state_province]'),
			zipcode=request.POST.get('data[zipcode]'),
			country='US',
			rev_share_perc=0.5
		)
		business.save()
		profile.business = business
		profile.save()

		# create managed stripe account
		account = create_managed_stripe_account(user, business)

	# add user to business owners group
	g = Group.objects.get(name='Business Owners')
	g.user_set.add(user)

	data = {'found_user': True, 'account_id': account.id}
	return JsonResponse(data)


@login_required(login_url='/sign-in/')
def ajax_stripe_legal_details(request):
	"""

	"""
	# get stripe account details
	stripe.api_key = settings.STRIPE_API_SECRET
	acct = stripe.Account.retrieve(request.POST.get('account_id'))

	# update details for legal entity
	acct.legal_entity.type = request.POST.get('data[company_legal_type]')
	acct.legal_entity.business_name = request.POST.get('data[company_legal_name]')
	acct.legal_entity.business_tax_id = request.POST.get('data[tin]')
	try:
		acct.legal_entity.dob.month = request.POST.get('data[dob]').split('/')[0]
		acct.legal_entity.dob.day = request.POST.get('data[dob]').split('/')[1]
		acct.legal_entity.dob.year = request.POST.get('data[dob]').split('/')[2]
	except IndexError:
		acct.legal_entity.dob.month = request.POST.get('data[dob]')[:2]
		acct.legal_entity.dob.day = request.POST.get('data[dob]')[2:4]
		acct.legal_entity.dob.year = request.POST.get('data[dob]')[4:]
	acct.legal_entity.ssn_last_4 = request.POST.get('data[last_4_ssn]')
	acct.save()

	data = {'account_id': acct.id}
	return JsonResponse(data)


@login_required(login_url='/sign-in/')
def ajax_stripe_tos_external_account(request):
	"""

	"""
	# get stripe account details
	stripe.api_key = settings.STRIPE_API_SECRET
	acct = stripe.Account.retrieve(request.POST.get('account_id'))

	# sign stripe terms of service
	acct.tos_acceptance.date = int(time.time())
	acct.tos_acceptance.ip = ajax_get_client_ip(request)
	acct.save()

	# add external bank account
	bank_account = acct.external_accounts.create(
		external_account={
			'object': 'bank_account',
			'country': 'US',
			'currency': 'USD',
			'routing_number': request.POST.get('data[routing_number]'),
			'account_number': request.POST.get('data[account_number1]')
		}
	)

	data = {'bank_account': bank_account}
	return JsonResponse(data)


@login_required(login_url='/sign-in/')
def ajax_get_client_ip(request):
	"""
	Get client IP and return JSON containing value
	"""
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip
