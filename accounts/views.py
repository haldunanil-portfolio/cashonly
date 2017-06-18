from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.forms import RegistrationForm
from accounts.forms import ProfileForm
from accounts.forms import BusinessForm
from accounts.decorators import not_loggedin_required
from accounts.decorators import profile_does_not_exist
from django.contrib import messages
from accounts.stripe import create_managed_stripe_account
from accounts.stripe import create_customer_stripe_account
from django.contrib.auth.models import Group
from transactions.models import CustomerBalance


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
	referer = request.META.get('HTTP_REFERER', '')
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
	if request.method == 'POST':
		form = BusinessForm(request.POST)
		if form.is_valid():
			# get existing info
			user = request.user
			profile = request.user.profile

			# associate user with business
			business = form.save(commit=False)
			business.country = 'US'
			business.rev_share_perc = 0.5
			form.save()
			profile.business = business
			profile.save()

			# add user to business owners group
			g = Group.objects.get(name='Business Owners')
			g.user_set.add(user)

			# create managed stripe account
			account = create_managed_stripe_account(user, business)

			# return message on the next page
			messages.info(request, 'Thanks for signing up as a business! Check your email for updates :)')
			return redirect('/')

	else:
		form = BusinessForm()

	return render(request, 'business-sign-up.html', {'form': form})
