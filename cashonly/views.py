from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib import messages
from django.template import RequestContext
from accounts.views import registration_next_steps


def is_member(user, group):
	'''
	Helper function to determine whether a user belongs to a single group
	'''
	return user.groups.filter(name=group).exists()


def is_in_multiple_groups(user, list_of_groups):
	'''
	Helper function to determine whether a user belongs to multiple groups
	'''
	permList = [is_member(user, group) for group in list_of_groups]

	if False not in permList:
		return True

	return False


def home(request):
	'''
	View method for homepage
	'''
	if request.user.is_authenticated:
		# Validate that a profile exists for user, if not force creation
		if not hasattr(request.user, 'profile'):
			return redirect('/sign-up/more-details/')

		# Check is user belongs to both the "Consumer" and "Business" groups
		if is_in_multiple_groups(request.user, ['Consumers', 'Business Employees']):
			pass ## to be developed

		# Check if user belongs to the "Consumers" group
		elif is_member(request.user, 'Consumers'):
			return render(request, 'base.html')

		# Check if user belongs to the "Businesses" group
		elif is_member(request.user, 'Business Employees'):
			pass ## to be developed

		# Handle situation where user belongs to none of the groups
		else:
			logout(request)
			messages.info(request, 'ERROR: You do not belong to any group, please contact <a href="mailto:admin@cashon.ly">admin@cashon.ly</a> for assistance.')

	return render(request, 'base.html')

def handler404(request):
	'''
	Page to display when user sent to URI that doesn't exist; 404 response
	'''
	return render(request, '404.html', status=404)
