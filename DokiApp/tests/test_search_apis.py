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
        'fullname': 'OG LOC', 'sex': 'U', 'profile_picture_url': None, 'medical_degree_photo': None,
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
     'sex': 'U', 'profile_picture_url': None, 'degree': 'general', 'medical_degree_photo': None, 'cv': 'default',
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
    fixtures = ['tags.json', 'doctors.json', 'doctor_profiles.json', 'expertises.json']

    def setup_more_doctors_and_tags(self):
        tag = Tag.objects.get(title='Oncologist')
        for i in range(40):
            doctor = mixer.blend('DokiApp.User', is_doctor=True)
            doctorProfile = mixer.blend('DokiApp.DoctorProfile', user=doctor)
            mixer.blend('DokiApp.Expertise', doctor=doctorProfile, tag=tag)

    def test_empty_keyword(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags//')
        self.assertEqual(response.status_code, 404)

    def test_space_keyword(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/ /')
        self.assertEqual(response.status_code, 404)

    def test_tag_does_not_exist(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/spam/')
        self.assertEqual(response.status_code, 404)

    def test_tag_is_not_complete(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/gi/')
        self.assertEqual(response.status_code, 404)

    def test_only_one_page_result(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Nephrologist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'max_page': 1,
                                         'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1]]})

    def test_case_sensitive(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/nephrologist/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'max_page': 1,
                                         'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1]]})

    def test_some_pages_result_the_first_page_default(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [i + 4 for i in range(1, 13)]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_some_pages_result_the_first_page_manual(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/?page=1')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [i + 4 for i in range(1, 13)]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_some_pages_result_a_middle_page(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/?page=2')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [i + 4 + 12 for i in range(1, 13)]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_some_pages_result_the_last_page(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/?page=4')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [41, 42, 43, 44]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_zero_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/?page=0')

        self.assertEqual(response.status_code, 404)

    def test_under_range_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/?page=-1')

        self.assertEqual(response.status_code, 404)

    def test_over_range_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/?page=5')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"success": False, "message": "Page not found", "max_page": 4})

    def test_no_results(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'tags/Oncologist/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'success': False, 'message': 'There is no doctors with the expertise.'})


class TestAdvancedSearch(TestCase):
    fixtures = ['tags.json', 'doctors.json', 'doctor_profiles.json', 'expertises.json']

    def setup_more_doctors_and_tags(self):
        tag = Tag.objects.get(title='Oncologist')
        for i in range(40):
            doctor = mixer.blend('DokiApp.User', is_doctor=True)
            doctorProfile = mixer.blend('DokiApp.DoctorProfile', user=doctor)
            mixer.blend('DokiApp.Expertise', doctor=doctorProfile, tag=tag)

    def test_empty_params(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [], 'page': 1, 'max_page': 1})

    def test_space_tags(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags= ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [], 'page': 1, 'max_page': 1})

    def test_space_name(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?name= ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[2], ALL_DOCTORS_LIST[3]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_space_sex(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex= ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [], 'page': 1, 'max_page': 1})

    def test_invalid_page(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&page=2')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'success': False, 'message': 'Page not found'})

    def test_invalid_sort(self):
        with self.assertRaises(Exception) as raised:
            self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&sort=spam')
        self.assertEqual(KeyError, type(raised.exception))

    def test_invalid_reverse(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&sort=username&reverse=spam')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_true_reverse(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&sort=username&reverse=1')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_false_reverse(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&sort=username')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[1], ALL_DOCTORS_LIST[0]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_tags(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_multi_tags(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist,Endocrinologist')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1], ALL_DOCTORS_LIST[2]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_name(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?name=Ali')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[3]], 'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_sex(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[1], ALL_DOCTORS_LIST[3]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_all_params_no_result(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&name=DRE&sex=U')
        self.assertEqual(response.data, {'doctors': [], 'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_all_params(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=Nephrologist&name=DRE&sex=P')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0]], 'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_case_sensitive(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?tags=nephrologist')
        self.assertEqual(response.data, {'doctors': [], 'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_name_case_sensitive(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?name=ali')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[3]], 'success': True, 'page': 1, 'max_page': 1})

    def test_found_by_sex_case_sensitive(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=p')
        self.assertEqual(response.data, {'doctors': [], 'success': True, 'page': 1, 'max_page': 1})

    def test_sort_by_sex(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sort=sex&name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[2]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_sort_by_fullname(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sort=fullname&name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[2]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_sort_by_email(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sort=email&name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[2]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_sort_by_sex_reverse(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sort=sex&reverse=1&name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[2], ALL_DOCTORS_LIST[0]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_sort_by_fullname_reverse(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sort=fullname&reverse=1&name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[2], ALL_DOCTORS_LIST[0]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_sort_by_email_reverse(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sort=email&reverse=1&name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[2], ALL_DOCTORS_LIST[0]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_only_one_page_result(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?name=e ')
        self.assertEqual(response.data, {'doctors': [ALL_DOCTORS_LIST[0], ALL_DOCTORS_LIST[2]],
                                         'success': True, 'page': 1, 'max_page': 1})

    def test_some_pages_result_max_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)

    def test_some_pages_result_the_first_page(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P&page=1')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_some_pages_result_a_middle_page(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P&page=2')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [i + 14 for i in range(12)]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_some_pages_result_the_last_page(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P&page=4')
        response_doctor_ids = [doctor['id'] for doctor in response.data['doctors']]
        doctor_ids = [38, 39, 40, 41, 42, 43, 44]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['max_page'], 4)
        self.assertEqual(response_doctor_ids, doctor_ids)

    def test_zero_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P&page=0')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"success": False, "message": "Page not found"})

    def test_under_range_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P&page=-1')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"success": False, "message": "Page not found"})

    def test_over_range_page_number(self):
        self.setup_more_doctors_and_tags()
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?sex=P&page=5')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"success": False, "message": "Page not found"})

    def test_no_results(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'search/?name=spam')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'doctors': [], 'page': 1, 'max_page': 1})
