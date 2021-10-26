from django.test import TestCase
from django.test import RequestFactory
from django.test import Client

from mixer.backend.django import mixer

from django.contrib.auth import authenticate
from django.contrib.auth import login

from ..views import *
from ..models import *


class TestSignUp(TestCase):

    def test_sign_up_api(self):
        data = {"username": "username_1",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "09372244222",
                "fullname": "the first user",
                "is_doctor": True}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {"success": True, "message": "User saved successfully"}
        self.assertEqual(response.data, response_result)

    def test_sign_up_saved_data(self):
        data = {"username": "username_1",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "09372244222",
                "fullname": "the first user",
                "is_doctor": False}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        SignUp.as_view()(request)
        user = User.objects.get(id=1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.is_doctor, False)
        self.assertEqual(user.is_patient, True)
        self.assertEqual(user.username, "username_1")
        self.assertEqual(user.email, "user_1@gmail.com")
        self.assertEqual(user.phone, "09372244222")
        self.assertEqual(user.fullname, "the first user")
        self.assertEqual(user.verified_email, False)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)

    def test_duplicated_username(self):
        mixer.blend('DokiApp.User', username="username_1")

        data = {"username": "username_1",
                "password": "password_2",
                "email": "user_2@gmail.com",
                "phone": "093722444444",
                "fullname": "the second user",
                "is_doctor": True}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message']['username'][0], 'user with this username already exists.')

    def test_duplicated_email(self):
        mixer.blend('DokiApp.User', email="user_1@gmail.com")

        data = {"username": "username_2",
                "password": "password_2",
                "email": "user_1@gmail.com",
                "phone": "093722444444",
                "fullname": "the second user",
                "is_doctor": True}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message']['email'][0], 'user with this email already exists.')

    def test_duplicated_phone(self):
        mixer.blend('DokiApp.User', phone="09372244222")

        data = {"username": "username_2",
                "password": "password_2",
                "email": "user_2@gmail.com",
                "phone": "09372244222",
                "fullname": "the second user",
                "is_doctor": True}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message']['phone'][0], 'user with this phone already exists.')

    def test_blank_username(self):
        data = {"username": "",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "09372244222",
                "fullname": "the first user",
                "is_doctor": True}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.data['message']['username'][0], 'This field may not be blank.')

    def test_invalid_email(self):
        INVALID_EMAILS = ["@gmail.com", "gmail.com", "a@gmail@com", "A@gmail", "InvalidEmail@.com"]

        data = {"username": "username_1",
                "password": "password_1",
                "email": "",
                "phone": "09372244222",
                "fullname": "the first user",
                "is_doctor": True}

        for email in INVALID_EMAILS:
            data["email"] = email
            request = RequestFactory().post('api/sign_up', data, content_type='application/json')
            response = SignUp.as_view()(request)
            self.assertEqual(response.data['message']['email'][0], 'Enter a valid email address.')

    def test_invalid_phone(self):
        INVALID_PHONES = ["16ewf54", "862+2", "+86331+34", "68+", "+853f77", "33"]

        data = {"username": "username_1",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "",
                "fullname": "the first user",
                "is_doctor": False}

        for phone in INVALID_PHONES:
            data["phone"] = phone
            data["username"] = "a" + data["username"]
            data["email"] = "a" + data["email"]
            request = RequestFactory().post('api/sign_up', data, content_type='application/json')
            response = SignUp.as_view()(request)
            self.assertEqual(response.data['message']['phone'][0], 'Invalid phone number')

    def test_long_phone(self):
        data = {"username": "username_1",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "+981235486498313688432168",
                "fullname": "the first user",
                "is_doctor": False}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.data['message']['phone'][0], 'Ensure this field has no more than 20 characters.')

    def test_valid_phone(self):
        VALID_PHONES = ["09123446548", "00989552345689", "+989213581456"]

        data = {"username": "username_1",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "",
                "fullname": "the first user",
                "is_doctor": False}

        for phone in VALID_PHONES:
            data["phone"] = phone
            data["username"] = "a" + data["username"]
            data["email"] = "a" + data["email"]
            request = RequestFactory().post('api/sign_up', data, content_type='application/json')
            response = SignUp.as_view()(request)
            response_result = {'success': True, 'message': 'User saved successfully'}
            self.assertEqual(response.data, response_result)

    def test_short_password(self):
        data = {"username": "a",
                "password": "p_1",
                "email": "user_1@gmail.com",
                "phone": "+989372223344",
                "fullname": "the first user",
                "is_doctor": False}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        response = SignUp.as_view()(request)
        self.assertEqual(response.data['message']['password'][0], 'Password is too short')

    def test_password_hashed(self):
        data = {"username": "a",
                "password": "12345",
                "email": "user_1@gmail.com",
                "phone": "+989372223344",
                "fullname": "the first user",
                "is_doctor": False}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        SignUp.as_view()(request)
        self.assertNotEqual(User.objects.get(id=1).password, "12345")


class TestLogIn(TestCase):

    def test_login(self):
        user = mixer.blend('DokiApp.User', username="user")
        user.set_password("password")
        user.verify_email()
        user.save()

        data = {"username": "user", "password": "password"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(list(response.data)[1], 'token')
        self.assertEqual(User.objects.get(id=1).auth_token.key, response.data['token'])

    def test_email_not_verified(self):
        user = mixer.blend('DokiApp.User', username="user")
        user.set_password("password")
        user.save()

        data = {"username": "user", "password": "password"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 405)
        response_result = {'success': False, 'message': 'Email is not verified'}
        self.assertEqual(response.data, response_result)

    def test_password_error(self):
        user = mixer.blend('DokiApp.User', username="user")
        user.set_password("password")
        user.verify_email()
        user.save()

        data = {"username": "user", "password": "wrong_password"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], "Unable to log in with provided credentials.")

    def test_username_error(self):
        user = mixer.blend('DokiApp.User', username="user")
        user.set_password("password")
        user.verify_email()
        user.save()

        data = {"username": "wrong_user", "password": "password"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], "Unable to log in with provided credentials.")

    def test_input_error(self):
        user = mixer.blend('DokiApp.User', username="user")
        user.set_password("password")
        user.verify_email()
        user.save()

        data = {"password": "password"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'This field is required.')
        self.assertEqual(len(response.data), 1)

        data = {"username": "user"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertEqual(len(response.data), 1)

        data = {}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'This field is required.')
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertEqual(len(response.data), 2)


class TestLogOut(TestCase):

    class CustomIsAuthenticated(IsAuthenticated):
        def has_permission(self, request, view):
            return bool(request.user)

    def setUp(self):
        user = mixer.blend('DokiApp.User', username="user")
        user.set_password("password")
        user.verify_email()
        user.save()

        data = {"username": "user", "password": "password"}
        request = RequestFactory().post('api/login', data, content_type='application/json')
        response = LogIn.as_view()(request)
        self.user = user
        self.token = response.data['token']

    def test_logout(self):
        request = RequestFactory().post('api/logout', {"username": "user"}, content_type='application/json')

        request.__setattr__('authed_user', self.user)
        LogOut.permission_classes = (self.CustomIsAuthenticated, )

        response = LogOut.as_view()(request)

    def test_not_authed(self):
        request = RequestFactory().post('api/logout', data={}, content_type='application/json')
        LogOut.permission_classes = (IsAuthenticated, )
        response = LogOut.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
