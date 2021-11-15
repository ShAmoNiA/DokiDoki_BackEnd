from django.test import TestCase
from django.test import RequestFactory
from django.test.client import encode_multipart

from mixer.backend.django import mixer

from django.contrib.auth import authenticate

from ..views import *
from ..models import *


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


class TestSearchForTag(TestCase):
    fixtures = ['tags.json']

    def test_all(self):
        data = {"key": ""}
        request = RequestFactory().post('api/search_by_tag', data, content_type='application/json')
        response = SearchForTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        tags = "Cardiologist Oncologist Gastroenterologist Pulmonologist Nephrologist " \
               "Endocrinologist Ophthalmologist Otolaryngologist Dermatologist " \
               "Psychiatrist Neurologist Radiologist Anesthesiologist Surgeon "
        response_result = {'success': True, 'tags': tags}
        self.assertEqual(response_result, response.data)

    def test_a_title(self):
        data = {"key": "ur"}
        request = RequestFactory().post('api/search_by_tag', data, content_type='application/json')
        response = SearchForTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        tags = "Neurologist Surgeon "
        response_result = {'success': True, 'tags': tags}
        self.assertEqual(response_result, response.data)

    def test_not_found(self):
        data = {"key": "a_title_that_there_is_not_in_saved_tags"}
        request = RequestFactory().post('api/search_by_tag', data, content_type='application/json')
        response = SearchForTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'tags': ''}
        self.assertEqual(response_result, response.data)


class TestSearchDoctorByName(TestCase):
    fixtures = ['doctors.json']

    def test_all(self):
        data = {"key": ""}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: {'username': 'DRE', 'password': '', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'DRE', 'sex': 'P'},
                   2: {'username': 'CJ', 'password': '', 'email': 'cj@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'CJ', 'sex': 'P'},
                   3: {'username': 'OG LOC', 'password': '', 'email': 'og.loc@gmail.com', 'is_doctor': True,
                       'profile_picture_url': None, 'phone': None, 'fullname': 'OG LOC', 'sex': 'P'},
                   4: {'username': 'Ali', 'password': '', 'email': 'ali@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'Ali sadeghi', 'sex': 'P'}}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_a_name(self):
        data = {"key": "rE"}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: {'username': 'DRE', 'password': '', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'DRE', 'sex': 'P'}}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

        data = {"key": "o"}
        request = RequestFactory().post('api/search_doctor_by_name', data, content_type='application/json')
        response = SearchDoctorByName.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: {'username': 'DRE', 'password': '', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'DRE', 'sex': 'P'},
                   2: {'username': 'CJ', 'password': '', 'email': 'cj@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'CJ', 'sex': 'P'},
                   3: {'username': 'OG LOC', 'password': '', 'email': 'og.loc@gmail.com', 'is_doctor': True,
                       'profile_picture_url': None, 'phone': None, 'fullname': 'OG LOC', 'sex': 'P'},
                   4: {'username': 'Ali', 'password': '', 'email': 'ali@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'Ali sadeghi', 'sex': 'P'}}
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
    fixtures = ['tags.json', 'doctors.json', 'doctor_profiles.json']

    def test_all(self):
        data = {"key": ""}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: {'username': 'DRE', 'password': '', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'DRE', 'sex': 'P'},
                   2: {'username': 'CJ', 'password': '', 'email': 'cj@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'CJ', 'sex': 'P'},
                   3: {'username': 'OG LOC', 'password': '', 'email': 'og.loc@gmail.com', 'is_doctor': True,
                       'profile_picture_url': None, 'phone': None, 'fullname': 'OG LOC', 'sex': 'P'},
                   4: {'username': 'Ali', 'password': '', 'email': 'ali@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'Ali sadeghi', 'sex': 'P'}}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_a_title(self):
        data = {"key": "Ey"}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        doctors = {1: {'username': 'DRE', 'password': '', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None,
                       'profile_picture_url': None, 'fullname': 'DRE', 'sex': 'P'},
                   3: {'username': 'OG LOC', 'password': '', 'email': 'og.loc@gmail.com', 'is_doctor': True,
                       'profile_picture_url': None, 'phone': None, 'fullname': 'OG LOC', 'sex': 'P'}}
        response_result = {'success': True, 'doctors': doctors}
        self.assertEqual(response_result, response.data)

    def test_not_found(self):
        data = {"key": "spam"}
        request = RequestFactory().post('api/search_doctor_by_tag', data, content_type='application/json')
        response = SearchDoctorByTag.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'doctors': {}}
        self.assertEqual(response_result, response.data)
