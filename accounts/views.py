from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from accounts.forms import RegistrationForm
from accounts.forms import ProfileForm
from accounts.forms import BusinessForm
from accounts.decorators import not_loggedin_required
from django.contrib import messages

@not_loggedin_required
def registration(request):
	'''
	Registration method
	'''
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			new_user = authenticate(username=form.cleaned_data['username'],
									password=form.cleaned_data['password1'])
			login(request, new_user)
			return redirect('/sign-up/more-details/')

	else:
		form = RegistrationForm()

	return render(request, 'auth_form.html', {'form': form})

@login_required(login_url='/sign-in/')
def registration_next_steps(request):
	'''
	'''
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			next_step = form.save(commit=False)
			next_step.user = request.user
			form.save()
			return redirect('/')

	elif 'sign-up' in request.META.get('HTTP_REFERER', ''):
		form = ProfileForm()
		return render(request, 'form-next-step.html', {'form': form})

	return redirect('/')

def signout(request):
	'''
	Sign out method
	'''
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
			profile = request.user.profile
			business = form.save(commit=False)
			business.country = 'US'
			form.save()

			profile.business = business
			profile.save()

			messages.info(request, 'Thanks for signing up! Stay tuned for updates :)')
			return redirect('/')

	else:
		form = BusinessForm()

	return render(request, 'business-sign-up.html', {'form': form})
