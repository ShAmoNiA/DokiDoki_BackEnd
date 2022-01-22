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
        'cv': 'default', 'office_location': None, 'rate': 0, 'comments_count': 0,
        'expertise_tags': 'Gastroenterologist Nephrologist Pulmonologist'},
    2: {'username': 'CJ', 'email': 'cj@gmail.com', 'is_doctor': True, 'phone': None, 'office_location': None,
        'sex': 'P', 'profile_picture_url': None, 'degree': 'general', 'medical_degree_photo': None, 'rate': 0,
        'cv': 'default', 'fullname': 'CJ', 'expertise_tags': 'Nephrologist Endocrinologist', 'comments_count': 0},
    3: {'username': 'OG LOC', 'email': 'og.loc@gmail.com', 'is_doctor': True, 'phone': None, 'degree': 'general',
        'fullname': 'OG LOC', 'sex': 'P', 'profile_picture_url': None, 'medical_degree_photo': None,
        'cv': 'default', 'office_location': None, 'rate': 0, 'comments_count': 0,
        'expertise_tags': 'Ophthalmologist Dermatologist Endocrinologist'},
    4: {'username': 'Ali', 'email': 'ali@gmail.com', 'is_doctor': True, 'phone': None, 'rate': 0,
        'fullname': 'Ali sadeghi', 'sex': 'P', 'profile_picture_url': None, 'degree': 'general', 'comments_count': 0,
        'medical_degree_photo': None, 'cv': 'default', 'office_location': None, 'expertise_tags': ''}
}

ALL_DOCTORS_LIST = [
    {'username': 'DRE', 'email': 'dre@gmail.com', 'is_doctor': True, 'phone': None, 'fullname': 'DRE', 'sex': 'P',
     'profile_picture_url': 'default.png', 'degree': 'general', 'medical_degree_photo': None, 'cv': 'default',
     'office_location': None, 'expertise_tags': 'Gastroenterologist Nephrologist Pulmonologist', 'rate': 0,
     'comments_count': 0, 'id': 1},
    {'username': 'CJ', 'email': 'cj@gmail.com', 'is_doctor': True, 'phone': None, 'fullname': 'CJ', 'sex': 'P',
     'profile_picture_url': None, 'degree': 'general', 'medical_degree_photo': None, 'cv': 'default',
     'office_location': None, 'expertise_tags': 'Nephrologist Endocrinologist', 'rate': 0, 'comments_count': 0,
     'id': 2},
    {'username': 'OG LOC', 'email': 'og.loc@gmail.com', 'is_doctor': True, 'phone': None, 'fullname': 'OG LOC',
     'sex': 'P', 'profile_picture_url': None, 'degree': 'general', 'medical_degree_photo': None, 'cv': 'default',
     'office_location': None, 'expertise_tags': 'Ophthalmologist Dermatologist Endocrinologist', 'rate': 0,
     'comments_count': 0, 'id': 3},
    {'username': 'Ali', 'email': 'ali@gmail.com', 'is_doctor': True, 'phone': None, 'fullname': 'Ali sadeghi',
     'sex': 'P', 'profile_picture_url': None, 'degree': 'general', 'medical_degree_photo': None, 'cv': 'default',
     'office_location': None, 'expertise_tags': '', 'rate': 0, 'comments_count': 0, 'id': 4}]


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


class TestSearchDoctorByKeyword(TestCase):
    fixtures = ['tags.json', 'doctors.json', 'doctor_profiles.json', 'expertises.json']

    def test_no_keyword(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search')
        self.assertEqual(response.status_code, 301)

    def test_empty_keyword(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search//')
        self.assertEqual(response.status_code, 404)

    def test_space_keyword(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/ /')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {'success': True, 'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[2], ALL_DOCTORS_LIST[3]]})

    def test_keyword_contains_fullname(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/sadeghi/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [ALL_DOCTORS_LIST[3]]})

    def test_keyword_contains_first_name(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/Toosh mooze/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [ALL_DOCTORS_LIST[3]]})

    def test_keyword_contains_last_name(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/mooz!/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [ALL_DOCTORS_LIST[3]]})

    def test_keyword_contains_username(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/Ali/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [ALL_DOCTORS_LIST[3]]})

    def test_keyword_contains_tag(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/Ali/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [ALL_DOCTORS_LIST[3]]})

    def test_keyword_contains_name_and_tag_both(self):
        for e in Expertise.objects.filter(doctor=User.objects.get(username='DRE').profile):
            e.delete()

        response = self.client.get(LOCALHOST_BASE_URL + 'search/ro/')
        self.assertEqual(response.status_code, 200)
        doctor_1_result = dict({})
        for k, v in ALL_DOCTORS_LIST[0].items():
            if k == 'expertise_tags':
                v = ''
            doctor_1_result[k] = v

        self.assertEqual(response.data, {'success': True, 'doctors': [doctor_1_result, ALL_DOCTORS_LIST[1]]})

    def test_no_results(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/spam/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': []})


class TestSearchDoctorsWithTag(TestCase):

    def test_empty_keyword(self):
        pass

    def test_space_keyword(self):
        pass

    def test_only_one_page_result(self):
        pass

    def test_some_pages_result_max_page_number(self):
        pass

    def test_some_pages_result_the_first_page(self):
        pass

    def test_some_pages_result_a_middle_page(self):
        pass

    def test_some_pages_result_the_last_page(self):
        pass

    def test_under_range_page_number(self):
        pass

    def test_over_range_page_number(self):
        pass

    def test_no_results(self):
        pass


class TestAdvancedSearch(TestCase):

    def test_empty_params(self):
        pass

    def test_space_tags(self):
        pass

    def test_space_name(self):
        pass

    def test_space_sex(self):
        pass

    def test_invalid_page(self):
        pass

    def test_invalid_sort(self):
        pass

    def test_invalid_reverse(self):
        pass

    def test_found_by_tags(self):
        pass

    def test_found_by_name(self):
        pass

    def test_found_by_sex(self):
        pass

    def test_found_by_all_params(self):
        pass

    def sort_by_sex(self):
        pass

    def sort_by_fullname(self):
        pass

    def sort_by_last_name(self):
        pass

    def sort_by_sex_reverse(self):
        pass

    def sort_by_fullname_reverse(self):
        pass

    def sort_by_last_name_reverse(self):
        pass

    def test_only_one_page_result(self):
        pass

    def test_some_pages_result_max_page_number(self):
        pass

    def test_some_pages_result_the_first_page(self):
        pass

    def test_some_pages_result_a_middle_page(self):
        pass

    def test_some_pages_result_the_last_page(self):
        pass

    def test_under_range_page_number(self):
        pass

    def test_over_range_page_number(self):
        pass

    def test_no_results(self):
        pass
