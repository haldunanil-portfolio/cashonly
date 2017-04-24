from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from accounts.forms import RegistrationForm, ProfileForm
from accounts.decorators import not_loggedin_required

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
