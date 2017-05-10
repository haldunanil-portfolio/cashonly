from django.test import TestCase, Client
from django.contrib.auth import get_user
from django.contrib.auth.models import User, Group
from accounts.forms import RegistrationForm, ProfileForm


class RegistrationTests(TestCase):

    def test_registration_form_valid(self):
        '''
        Valid user should be successfully created after entering
        all required fields.
        '''
        form_data = {'username': 'test@example.com',
                     'first_name': 'Test',
                     'last_name': 'Person',
                     'password1': 'test1234',
                     'password2': 'test1234'}

        form = RegistrationForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_registration_form_invalid(self):
        '''
        Invalid user should not be created after entering the
        required fields.
        '''
        form_data = {'username': '',
                     'first_name': '',
                     'last_name': '',
                     'password1': 'pw',
                     'password2': 'pw'}

        form = RegistrationForm(data=form_data)

        self.assertFalse(form.is_valid())

    def test_registration_view(self):
        '''
        Tests whether user registration view calls the right template.
        '''
        response = self.client.get("/sign-up/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_form.html")

    def test_registration_valid_view(self):
        '''
        Test whether registration form properly creates a user.
        '''
        user_count = User.objects.count()
        form_data = {'username': 'test@example.com',
                     'first_name': 'Test',
                     'last_name': 'Person',
                     'password1': 'admin123',
                     'password2': 'admin123'}

        consumers = Group.objects.create(name="Consumers")
        response = self.client.post("/sign-up/",
                                    form_data)

        self.assertEqual(User.objects.count(), user_count+1)

    def test_registration_invalid_view(self):
        '''
        Test whether an invalid registration form does NOT create a user.
        '''
        user_count = User.objects.count()
        form_data = {'username': '',
                     'first_name': '',
                     'last_name': '',
                     'password1': 'pw',
                     'password2': 'pw'}

        consumers = Group.objects.create(name="Consumers")
        response = self.client.post("/sign-up/",
                                    form_data)

        self.assertEqual(User.objects.count(), user_count)

    def test_not_logged_in(self):
        '''
        User should only be able to register if they are
        not already logged in.
        '''
        # first, attempt to access sign up page while not
        # logged in
        response = self.client.get('/sign-up/')
        self.assertEqual(response.status_code, 200)

        # next, create user
        username, pw = 'test@example.com', 'test1234'
        user = User.objects.create_user(username, password=pw)
        user.save()

        self.client.post('/sign-in/', {'username': username,
                                       'password': pw})

        # check that user is logged in
        user_li = get_user(self.client)
        self.assertTrue(user_li.is_authenticated())

        # attempt to visit sign up page while logged in
        response_li = self.client.get('/sign-up/')
        self.assertRedirects(response_li, '/', target_status_code=302)

        # next sign out
        self.client.get('/sign-out/', )

        # last, attempt to revisit sign up page after logout
        response_lo = self.client.get('/sign-up/')
        self.assertEqual(response_lo.status_code, 200)


class ProfileCreationTests(TestCase):
    """
    Must successfully create a profile after sign up regardless of method
    """
    def test_manual_sign_up(self):
        """

        """
        pass

    def test_facebook_sign_up(self):
        """

        """
        pass

    def test_google_sign_up(self):
        """

        """
        pass


class SignOutTests(TestCase):

    def test_sign_out_successfully(self):
        '''
        User should be successfully signed out when visiting
        /sign-out/ and redirected to home.
        '''
        username, pw = 'test@example.com', 'test1234'
        user = User.objects.create_user(username, password=pw)
        user.save()

        self.client.post('/sign-in/', {'username': username,
                                       'password': pw})

        # check that user is logged in
        user_li = get_user(self.client)
        self.assertTrue(user_li.is_authenticated())

        response = self.client.get('/sign-out/')
        user_lo = get_user(self.client)

        # check that user is logged out and redirected to home
        self.assertRedirects(response, '/')
        self.assertFalse(user_lo.is_authenticated())
