from django.test import TestCase
from django.test import RequestFactory

from mixer.backend.django import mixer

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
