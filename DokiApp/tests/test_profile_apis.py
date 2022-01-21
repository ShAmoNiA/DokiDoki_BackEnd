import os
from shutil import copyfile as copy

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import encode_multipart

from mixer.backend.django import mixer

from django.contrib.auth import authenticate

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'

COMPLETE_PROFILE_PATIENT = {'username': 'patient_1', 'fullname': 'patient_1', 'sex': 'P',
                            'is_doctor': False, 'phone': None, 'email': 'patient_1@gmail.com', 'weight': 0,
                            'profile_picture_url': "default.png", 'height': 0, 'medical_records': 'nothing yet'}
COMPLETE_PROFILE_DOCTOR = {'comments_count': 0, 'cv': 'default', 'username': 'DRE', 'email': 'dre@gmail.com',
                           'is_doctor': True, 'phone': None, 'fullname': 'DRE', 'sex': 'P', 'rate': 0,
                           'medical_degree_photo': None, 'office_location': None, 'profile_picture_url': "default.png",
                           'degree': 'general', 'expertise_tags': 'Gastroenterologist Nephrologist Pulmonologist'}

SAFE_PROFILE_PATIENT = dict(COMPLETE_PROFILE_PATIENT)
SAFE_PROFILE_DOCTOR = dict(COMPLETE_PROFILE_DOCTOR)
SAFE_PROFILE_PATIENT.pop('phone')
SAFE_PROFILE_DOCTOR.pop('phone')


class TestProfilePreview(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json',
                'tags.json', 'expertises.json']

    def test_preview_patient(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'profile_preview' + '?username=patient_1')

        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'profile': SAFE_PROFILE_PATIENT}
        self.assertEqual(response.data, response_result)

    def test_preview_doctor(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'profile_preview' + '?username=DRE')

        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'profile': SAFE_PROFILE_DOCTOR}
        self.assertEqual(response.data, response_result)

    def test_not_found(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'profile_preview' + '?username=spam')
        self.assertEqual(response.status_code, 404)


class TestMyProfilePreview(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json',
                'tags.json', 'expertises.json']

    def test_doctor_profile(self):
        self.client.force_login(User.objects.get(id=1))
        response = self.client.get(LOCALHOST_BASE_URL + 'my_profile_preview')

        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'profile': COMPLETE_PROFILE_DOCTOR}
        self.assertEqual(response.data, response_result)

    def test_patient_profile(self):
        self.client.force_login(User.objects.get(id=5))
        response = self.client.get(LOCALHOST_BASE_URL + 'my_profile_preview')

        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'profile': COMPLETE_PROFILE_PATIENT}
        self.assertEqual(response.data, response_result)


class TestEditProfile(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json']

    def setUp(self):
        mixer.blend('DokiApp.Tag', title="ddd")
        mixer.blend('DokiApp.Tag', title="aaa")
        mixer.blend('DokiApp.Tag', title="eee")

    def test_not_authed(self):
        request = RequestFactory().post('api/edit_profile', content_type='application/json')
        response = EditProfile.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_change_doctor_profile(self):
        self.client.force_login(User.objects.get(id=1))
        data = {'degree': 'NEW degree', 'cv': 'NEW cv', 'office_location': '021',
                'fullname': 'NEW fullname', 'medical_degree_photo': "THE URL"}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 200)
        response_result = {"success": True, "message": "Profile changed successfully"}
        self.assertEqual(response.data, response_result)

    def test_change_patient_profile(self):
        self.client.force_login(User.objects.get(id=5))
        data = {'fullname': 'NEW fullname', 'weight': 70, 'height': 175, 'medical_records': "NEW record"}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 200)
        response_result = {"success": True, "message": "Profile changed successfully"}
        self.assertEqual(response.data, response_result)

    def test_invalid_patient_weight(self):
        self.client.force_login(User.objects.get(id=5))
        data = {'weight': 17}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['weight'][0]), 'Enter Weight in kilograms')

    def test_invalid_patient_height(self):
        self.client.force_login(User.objects.get(id=5))
        data = {'height': 23}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['height'][0]), 'Enter height in centimeters')

    def test_invalid_patient_weight_and_height(self):
        self.client.force_login(User.objects.get(id=5))
        data = {'weight': 503, 'height': 273}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data['weight'][0]), 'Enter Weight in kilograms')
        self.assertEqual(str(response.data['height'][0]), 'Enter height in centimeters')

    def test_doctor_profile_updated(self):
        self.client.force_login(User.objects.get(id=1))
        data = {'degree': 'NEW degree', 'cv': 'NEW cv', 'office_location': '021', 'expertise_tags': 'ddd aaa eee',
                'fullname': 'NEW fullname', 'medical_degree_photo': "THE URL"}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        profile = DoctorProfile.objects.get(id=1)
        self.assertEqual(profile.degree, 'NEW degree')
        self.assertEqual(profile.medical_degree_photo, "THE URL")
        self.assertEqual(profile.cv, 'NEW cv')
        self.assertEqual(profile.office_location, '021')

    def test_patient_profile_updated(self):
        self.client.force_login(User.objects.get(id=5))
        data = {'fullname': 'NEW fullname', 'weight': 70, 'height': 175, 'medical_records': "NEW record"}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        profile = PatientProfile.objects.get(id=1)
        self.assertEqual(profile.weight, 70)
        self.assertEqual(profile.height, 175)
        self.assertEqual(profile.medical_records, "NEW record")

    def test_doctor_user_updated(self):
        self.client.force_login(User.objects.get(id=1))
        data = {'degree': 'NEW degree', 'cv': 'NEW cv', 'office_location': '021', 'expertise_tags': 'ddd aaa eee',
                'fullname': 'NEW fullname', 'medical_degree_photo': "THE URL"}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        user = User.objects.get(id=1)
        self.assertEqual(user.fullname, 'NEW fullname')

    def test_patient_user_updated(self):
        self.client.force_login(User.objects.get(id=5))
        data = {'fullname': 'NEW fullname', 'weight': 70, 'height': 175, 'medical_records': "NEW record"}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        user = User.objects.get(id=5)
        self.assertEqual(user.fullname, 'NEW fullname')

    def test_dangerous_keys(self):
        initial_user = User.objects.get(id=1)
        initial_profile = DoctorProfile.objects.get(id=1)
        self.client.force_login(initial_user)
        data = {'is_doctor': False, 'email': 'a@g.com', 'password': '1111', 'username': 'new_username',
                'user': User.objects.get(id=5), 'reset_password_token': 'new_token', 'verify_email_token': "NEW_TOKEN"}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        profile = DoctorProfile.objects.get(id=1)
        user = User.objects.get(id=1)
        self.assertEqual(user.is_doctor, initial_user.is_doctor)
        self.assertEqual(user.email, initial_user.email)
        self.assertEqual(user.password, initial_user.password)
        self.assertEqual(user.username, initial_user.username)
        self.assertEqual(user.reset_password_token, initial_user.reset_password_token)
        self.assertEqual(user.verify_email_token, initial_user.verify_email_token)
        self.assertEqual(profile.user, initial_profile.user)

        initial_user = User.objects.get(id=5)
        initial_profile = PatientProfile.objects.get(id=1)
        self.client.force_login(initial_user)
        data = {'is_doctor': False, 'email': 'a@g.com', 'password': '1111', 'username': 'new_username',
                'user': User.objects.get(id=1), 'reset_password_token': 'new_token', 'verify_email_token': "NEW_TOKEN"}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        profile = PatientProfile.objects.get(id=1)
        user = User.objects.get(id=5)
        self.assertEqual(user.is_doctor, initial_user.is_doctor)
        self.assertEqual(user.email, initial_user.email)
        self.assertEqual(user.password, initial_user.password)
        self.assertEqual(user.username, initial_user.username)
        self.assertEqual(user.reset_password_token, initial_user.reset_password_token)
        self.assertEqual(user.verify_email_token, initial_user.verify_email_token)
        self.assertEqual(profile.user, initial_profile.user)


class TestChangeProfileImage(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json', 'images.json']

    def restore_image(self):
        original = os.getcwd() + '\\default.png'
        target = os.getcwd() + r'\static\images\default.png'
        copy(original, target)

    def test_image_changed(self):
        self.client.force_login(User.objects.get(id=1))
        data = {'profile_picture_url': 'NEW_image_url'}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 200)
        response_result = {"success": True, "message": "Profile changed successfully"}
        self.assertEqual(response.data, response_result)
        self.assertEqual(User.objects.get(id=1).profile_picture_url, "NEW_image_url")

        self.restore_image()

    def test_the_same_image(self):
        user = User.objects.get(id=1)
        self.client.force_login(user)
        profile_picture_url = user.profile_picture_url
        data = {'profile_picture_url': profile_picture_url}
        response = self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(response.status_code, 200)
        response_result = {"success": True, "message": "Profile changed successfully"}
        self.assertEqual(response.data, response_result)

        self.assertEqual(User.objects.get(id=1).profile_picture_url, profile_picture_url)

    def test_old_image_deleted_from_database(self):
        self.client.force_login(User.objects.get(id=1))
        data = {'profile_picture_url': 'NEW_image_url'}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(Image.objects.all().count(), 0)

        self.restore_image()

    def test_old_image_deleted_from_files(self):
        self.client.force_login(User.objects.get(id=1))
        data = {'profile_picture_url': 'NEW_image_url'}
        self.client.post(LOCALHOST_BASE_URL + 'edit_profile', data)

        self.assertEqual(Image.objects.all().count(), 0)
        self.assertFalse(os.path.isfile(os.getcwd() + r'\static\images\default.png'))

        self.restore_image()


class TestAddExpertise(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json',
                'tags.json', 'expertises.json']

    def test_not_authed(self):
        response = self.client.post(LOCALHOST_BASE_URL + 'add_expertise')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_not_doctor(self):
        self.client.force_login(User.objects.get(id=5))
        response = self.client.post(LOCALHOST_BASE_URL + 'add_expertise')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_tag_not_found(self):
        self.client.force_login(User.objects.get(id=1))
        data = {"image_url": "the_url", "tag": "spam"}
        response = self.client.post(LOCALHOST_BASE_URL + 'add_expertise', data=data)

        self.assertEqual(response.status_code, 404)

    def test_response(self):
        self.client.force_login(User.objects.get(id=1))
        data = {"image_url": "the_url", "tag": "Radiologist"}
        response = self.client.post(LOCALHOST_BASE_URL + 'add_expertise', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Expertise saved successfully'})

    def test_data_saved(self):
        self.client.force_login(User.objects.get(id=1))
        data = {"image_url": "the_url", "tag": "Radiologist"}
        response = self.client.post(LOCALHOST_BASE_URL + 'add_expertise', data=data)

        self.assertEqual(response.status_code, 200)
        experience = Expertise.objects.get(id=9)
        self.assertEqual(experience.image_url, "the_url")
        self.assertEqual(experience.tag.title, "Radiologist")
        self.assertEqual(experience.doctor, DoctorProfile.objects.get(id=1))

    def test_repetitive_tag(self):
        self.client.force_login(User.objects.get(id=1))
        data = {"image_url": "the_url", "tag": "Radiologist"}
        self.client.post(LOCALHOST_BASE_URL + 'add_expertise', data=data)
        response = self.client.post(LOCALHOST_BASE_URL + 'add_expertise', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"success": True, "message": "You have recorded the expertise before"})
