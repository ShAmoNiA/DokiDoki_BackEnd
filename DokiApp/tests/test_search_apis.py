from django.test import TestCase
from django.test import RequestFactory
from django.test.client import encode_multipart

from mixer.backend.django import mixer

from django.contrib.auth import authenticate

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'

ALL_DOCTORS_PROFILES = {
    1: {'username': 'DRE', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None, 'fullname': 'DRE',
        'sex': 'P', 'profile_picture_url': "default.png", 'degree': 'general', 'medical_degree_photo': None,
        'cv': 'default', 'office_location': None, 'rate': None, 'comments_count': 0,
        'expertise_tags': 'Gastroenterologist Nephrologist Pulmonologist'},
    2: {'username': 'CJ', 'email': 'cj@gmail.com', 'is_doctor': True, 'phone': None,  'office_location': None,
        'sex': 'P', 'profile_picture_url': None, 'degree': 'general', 'medical_degree_photo': None, 'rate': None,
        'cv': 'default', 'fullname': 'CJ', 'expertise_tags': 'Nephrologist Endocrinologist', 'comments_count': 0},
    3: {'username': 'OG LOC', 'email': 'og.loc@gmail.com', 'is_doctor': True, 'phone': None, 'degree': 'general',
        'fullname': 'OG LOC', 'sex': 'P', 'profile_picture_url': None, 'medical_degree_photo': None,
        'cv': 'default', 'office_location': None, 'rate': None, 'comments_count': 0,
        'expertise_tags': 'Ophthalmologist Dermatologist Endocrinologist'},
    4: {'username': 'Ali', 'email': 'ali@gmail.com', 'is_doctor': True, 'phone': None, 'rate': None,
        'fullname': 'Ali sadeghi', 'sex': 'P', 'profile_picture_url': None, 'degree': 'general', 'comments_count': 0,
        'medical_degree_photo': None, 'cv': 'default', 'office_location': None, 'expertise_tags': ''}
}


class TestSearchForTag(TestCase):
    fixtures = ['tags.json']

    def test_all_tags(self):
        request = RequestFactory().get('api/all_tags')
        response = AllTags.as_view()(request)
        self.assertEqual(response.status_code, 200)
        tags = "Cardiologist Oncologist Gastroenterologist Pulmonologist Nephrologist " \
               "Endocrinologist Ophthalmologist Otolaryngologist Dermatologist " \
               "Psychiatrist Neurologist Radiologist Anesthesiologist Surgeon"
        response_result = {'success': True, 'tags': tags}
        self.assertEqual(response_result, response.data)


class TestSearchDoctorByName(TestCase):
    fixtures = ['doctors.json', 'doctor_profiles.json',
                'tags.json', 'expertises.json']

    def test_all(self):
        data = {"key": ""}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = ALL_DOCTORS_PROFILES
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_a_name(self):
        data = {"key": "rE"}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: ALL_DOCTORS_PROFILES[1]}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

        data = {"key": "o"}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = ALL_DOCTORS_PROFILES
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_not_found(self):
        data = {"key": "dogg"}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'doctors': {}}
        self.assertEqual(response_result, response.data)


class TestSearchDoctorByTag(TestCase):
    fixtures = ['tags.json', 'doctors.json', 'doctor_profiles.json', 'expertises.json']

    def test_all(self):
        self.maxDiff=None
        data = {"key": ""}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = ALL_DOCTORS_PROFILES
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_a_title(self):
        data = {"key": "Endocrinologist"}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {2: ALL_DOCTORS_PROFILES[2], 3: ALL_DOCTORS_PROFILES[3]}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_some_title(self):
        data = {"key": "Gastroenterologist Nephrologist"}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: ALL_DOCTORS_PROFILES[1], 2: ALL_DOCTORS_PROFILES[2]}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_not_found(self):
        data = {"key": "spam"}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'doctors': {}}
        self.assertEqual(response_result, response.data)

    def test_not_complete_key(self):
        data = {"key": "Gastroe"}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'doctors': {}}
        self.assertEqual(response_result, response.data)
