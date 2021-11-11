from django.test import TestCase
from django.test import RequestFactory
from django.test import Client
from django.test.client import encode_multipart

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

    def test_profile_created(self):
        data = {"username": "username_1",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "09372244222",
                "fullname": "the first user",
                "is_doctor": False}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        SignUp.as_view()(request)
        patient_user = User.objects.get(id=1)

        data = {"username": "username_2",
                "password": "password_2",
                "email": "user_2@gmail.com",
                "phone": "09372244322",
                "fullname": "the second user",
                "is_doctor": True}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        SignUp.as_view()(request)
        doctor_user = User.objects.get(id=2)

        patient_profile = PatientProfile.objects.get(id=1)
        doctor_profile = DoctorProfile.objects.get(id=1)
        self.assertEqual(patient_profile.user, patient_user)
        self.assertEqual(doctor_profile.user, doctor_user)

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

    def test_invalid_username(self):
        INVALID_USERNAMES = ["4name", ".name", "_name", "user_.name", "user._name", "user__name", "user..name",
                             "user$name", "user#name", "user@name", "user!name", "user&name", "user^name"]

        data = {"username": "username",
                "password": "password_1",
                "email": "user_1@gmail.com",
                "phone": "09372244222",
                "fullname": "the first user",
                "is_doctor": True}

        for username in INVALID_USERNAMES:
            data["username"] = username
            request = RequestFactory().post('api/sign_up', data, content_type='application/json')
            response = SignUp.as_view()(request)
            self.assertEqual(response.data['message']['username'][0], 'username is invalid')

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
                "password": "12345678",
                "email": "user_1@gmail.com",
                "phone": "+989372223344",
                "fullname": "the first user",
                "is_doctor": False}
        request = RequestFactory().post('api/sign_up', data, content_type='application/json')
        SignUp.as_view()(request)
        self.assertNotEqual(User.objects.get(id=1).password, "12345678")


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
        response_result = {'success': True, 'message': 'logged out successfully.'}
        self.assertEqual(response.data, response_result)

    def test_logout_failure(self):
        request = RequestFactory().post('api/logout', content_type='application/json')
        request.__setattr__('authed_user', self.user)
        LogOut.permission_classes = (self.CustomIsAuthenticated,)

        LogOut.as_view()(request)

    def test_not_authed(self):
        request = RequestFactory().post('api/logout', data={}, content_type='application/json')
        LogOut.permission_classes = (IsAuthenticated, )
        response = LogOut.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')


class TestVerifyEmail(TestCase):

    def test_verify_email(self):
        mixer.blend('DokiApp.User', email="e@gmail.com", verify_email_token="the_token")
        data = {"email": "e@gmail.com", "token": "the_token"}
        request = RequestFactory().post('api/verify_email', data, content_type='application/json')
        response = VerifyEmail.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your email verified successfully")
        self.assertTrue(User.objects.get(id=1).verified_email)

    def test_verified_before(self):
        user = mixer.blend('DokiApp.User', email="e@gmail.com", verify_email_token="the_token")
        user.verify_email()
        data = {"email": "e@gmail.com", "token": "the_token"}
        request = RequestFactory().post('api/verify_email', data, content_type='application/json')
        response = VerifyEmail.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ERROR: your email verified before")
        self.assertTrue(User.objects.get(id=1).verified_email)

    def test_token_error(self):
        mixer.blend('DokiApp.User', email="e@gmail.com", verify_email_token="the_token")
        data = {"email": "e@gmail.com", "token": "the_wrong_token"}
        request = RequestFactory().post('api/verify_email', data, content_type='application/json')
        response = VerifyEmail.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ERROR: privateTokenError")
        self.assertFalse(User.objects.get(id=1).verified_email)

    def test_no_such_user(self):
        mixer.blend('DokiApp.User', email="e@gmail.com", verify_email_token="the_token")
        data = {"email": "b@gmail.com", "token": "the_wrong_token"}
        request = RequestFactory().post('api/verify_email', data, content_type='application/json')
        with self.assertRaises(Exception) as raised:
            VerifyEmail.as_view()(request)
        self.assertEqual("<class 'DokiApp.models.User.DoesNotExist'>", str(type(raised.exception)))


class TestResetPassword(TestCase):

    def test_forgot_password(self):
        user = mixer.blend("DokiApp.User", email="e@gmail.com")
        user.verify_email()
        data = {"email": "e@gmail.com"}
        request = RequestFactory().get('api/forgot_password', data, content_type='application/json')
        response = forgot_password(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "email sent")
        self.assertEqual(len(User.objects.get(id=1).reset_password_token), 128)

    def test_forgot_password_wrong_email(self):
        user = mixer.blend("DokiApp.User", email="e@gmail.com")
        user.verify_email()
        data = {"email": "wrong@gmail.com"}
        request = RequestFactory().get('api/forgot_password', data, content_type='application/json')
        response = forgot_password(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user not found")

    def test_forgot_password_email_not_verified(self):
        mixer.blend("DokiApp.User", email="e@gmail.com")
        data = {"email": "e@gmail.com"}
        request = RequestFactory().get('api/forgot_password', data, content_type='application/json')
        response = forgot_password(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "email not verified")

    def test_reset_password(self):
        token = token_hex(32)
        mixer.blend('DokiApp.User', username="user", email="e@gmail.com",
                    verify_email_token="verified", reset_password_token=token)
        data = {"email": "e@gmail.com",
                "token": token,
                "password_1": "new_password",
                "password_2": "new_password"}
        request = RequestFactory().post('api/reset_password', data, content_type='application/json')
        response = ResetPassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password changed successfully. you can sign in.")
        user = User.objects.get(id=1)
        self.assertEqual(user.reset_password_token, "expired")
        self.assertEqual(authenticate(username="user", password="new_password"), user)

    def test_reset_password_wrong_email(self):
        mixer.blend('DokiApp.User', email="e@gmail.com")
        data = {"email": "wrong_e@gmail.com",
                "token": "token",
                "password_1": "new_password",
                "password_2": "new_password"}
        request = RequestFactory().post('api/reset_password', data, content_type='application/json')
        response = ResetPassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user not found")

    def test_reset_password_different_pass(self):
        mixer.blend('DokiApp.User', email="e@gmail.com")
        data = {"email": "e@gmail.com",
                "token": "token",
                "password_1": "new_password",
                "password_2": "new_password_2"}
        request = RequestFactory().post('api/reset_password', data, content_type='application/json')
        response = ResetPassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "passwords are different")

    def test_reset_password_email_not_verified(self):
        mixer.blend('DokiApp.User', email="e@gmail.com")
        data = {"email": "e@gmail.com",
                "token": "token",
                "password_1": "new_password",
                "password_2": "new_password"}
        request = RequestFactory().post('api/reset_password', data, content_type='application/json')
        response = ResetPassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your email is not verified")

    def test_reset_password_expired_token(self):
        mixer.blend('DokiApp.User', email="e@gmail.com", verify_email_token="verified")
        data = {"email": "e@gmail.com",
                "token": "token",
                "password_1": "new_password",
                "password_2": "new_password"}
        request = RequestFactory().post('api/reset_password', data, content_type='application/json')
        response = ResetPassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your token is expired")

    def test_reset_password_wrong_token(self):
        token_1 = token_hex(32)
        token_2 = token_hex(32)
        while token_1 == token_2:
            token_2 = token_hex(32)
        mixer.blend('DokiApp.User', email="e@gmail.com", verify_email_token="verified", reset_password_token=token_1)
        data = {"email": "e@gmail.com",
                "token": token_2,
                "password_1": "new_password",
                "password_2": "new_password"}
        request = RequestFactory().post('api/reset_password', data, content_type='application/json')
        response = ResetPassword.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your token is wrong")


class TestCheckUsername(TestCase):

    def test_exists(self):
        mixer.blend('DokiApp.User', username="user_1")
        request = RequestFactory().get('api/check_username')
        response = CheckUsername.as_view()(request, "user_1")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["exists"])

    def test_not_exists(self):
        request = RequestFactory().get('api/check_username')
        response = CheckUsername.as_view()(request, "user_1")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["exists"])


class TestSendEmail(TestCase):

    def test_send(self):
        EMAIL = "ntm.patronage@gmail.com"
        data = {"subject": "the_subject",
                "message": "the_message",
                "to_list": EMAIL}
        request = RequestFactory().post('api/send_email', data, content_type='application/json')
        response = send_email_by_front(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'message': 'email sent'}
        self.assertEqual(response.data, response_result)


class TestImageView(TestCase):

    @staticmethod
    def generate_photo_file():
        import os
        import io
        from PIL import Image as ImageCreator

        file = io.BytesIO()
        image = ImageCreator.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_upload_image(self):
        # TODO: fix this function
        photo_file = self.generate_photo_file()
        data = {'image': photo_file}

        request = RequestFactory().post('api/upload_image', data,
                                        content_type='multipart/form-data; boundary=<calculated when request is sent>')
        response = ImageView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        response_result = {"image_url": "/images/default.png"}
        self.assertEqual(response.data, response_result)

    def test_upload_image_default(self):
        request = RequestFactory().post('api/upload_image',
                                        content_type='multipart/form-data; boundary=<calculated when request is sent>')
        response = ImageView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        response_result = {"image_url": "/images/default.png"}
        self.assertEqual(response.data, response_result)


class TestAddTag(TestCase):

    def test_success(self):
        data = {"title": "the_title"}
        request = RequestFactory().post('api/add_tag', data, content_type='application/json')
        response = AddTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {"success": True, "message": "tag added successfully"}
        self.assertEqual(response_result, response.data)

    def test_data_saved(self):
        data = {"title": "the_title"}
        request = RequestFactory().post('api/add_tag', data, content_type='application/json')
        AddTag.as_view()(request)
        tag = Tag.objects.get(id=1)
        self.assertEqual(tag.title, "the_title")

    def test_invalid_title(self):
        data = {"title": "the title"}
        request = RequestFactory().post('api/add_tag', data, content_type='application/json')
        response = AddTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'message': 'tag not added', 'success': False}
        self.assertEqual(response_result, response.data)

    def test_empty_title(self):
        data = {"title": ""}
        request = RequestFactory().post('api/add_tag', data, content_type='application/json')
        response = AddTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'message': 'tag not added', 'success': False}
        self.assertEqual(response_result, response.data)

    def test_not_title(self):
        data = dict({})
        request = RequestFactory().post('api/add_tag', data, content_type='application/json')
        response = AddTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'message': 'tag not added', 'success': False}
        self.assertEqual(response_result, response.data)
