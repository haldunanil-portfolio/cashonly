from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib import messages
from django.template import RequestContext

def is_member(user, group):
	'''
	Helper function to determine whether a user belongs to a single group
	'''
	return user.groups.filter(name=group).exists()

def is_in_multiple_groups(user, list_of_groups):
	'''
	Helper function to determine whether a user belongs to multiple groups
	'''
	permList = [ is_member(user, group) for group in list_of_groups ]

	if False not in permList:
		return True

	return False

def home(request):
	'''
	View method for homepage
	'''
	if request.user.is_authenticated:
		# Check is user belongs to both the "Consumer" and "Business" groups
		if is_in_multiple_groups(request.user, ['Consumers', 'Businesses']):
			pass ## to be developed

		# Check if user belongs to the "Consumers" group
		elif is_member(request.user, 'Consumers'):
			return render(request, 'base.html')

		# Check if user belongs to the "Businesses" group
		elif is_member(request.user, 'Businesses'):
			pass ## to be developed

		# Handle situation where user belongs to none of the groups
		else:
			logout(request)
			messages.info(request, 'ERROR: You do not belong to any group, please contact administrator.')

	return render(request, 'base.html')

def handler404(request):
	'''
	Page to display when user sent to URI that doesn't exist; 404 response
	'''
	return render(request, '404.html', status=404)

def burger_test(request):
	return render(request, 'burger_test.html')
