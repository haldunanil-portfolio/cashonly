from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate, login
from accounts.forms import RegistrationForm

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
			return redirect('/')

	else:
		form = RegistrationForm()

	args = {'form': form}
	return render(request, 'auth_form.html', args)

def logout(request):
	'''
	Logout method
	'''
	django_logout(request)
	return redirect('/')