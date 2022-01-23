from django.test import TestCase

from mixer.backend.django import mixer

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'


class TestWriteComment(TestCase):

    def test_not_authed(self):
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment')

    def test_text_is_empty(self):
        # patient = User.objects.get(id=5)
        # self.client.force_login(patient)
        pass

    def test_text_is_space(self):
        pass

    def test_doctor_not_found(self):
        pass

    def test_comment_wrote(self):
        pass

    def test_comment_saved(self):
        pass


class TestGetComments(TestCase):
    fixtures = ['doctors.json', 'doctor_profiles.json', 'patients.json', 'comments.json']

    def test_no_comments(self):
        mixer.blend('DokiApp.User', is_doctor=True)
        response = self.client.get(LOCALHOST_BASE_URL + 'comments/9/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'comments': []})

    def test_comments_showed(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'comments/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'comments': [
            {'writer': 5, 'doctor': 1, 'text': 'It,s ok', 'date': '2014-09-01T09:50:30Z', 'writer_name': 'patient_1'},
            {'writer': 7, 'doctor': 1, 'text': 'It,s better', 'date': '2014-09-01T09:50:30Z',
             'writer_name': 'patient_3'}]})


class TestRateDoctor(TestCase):

    def test_not_authed(self):
        # response = self.client.post(LOCALHOST_BASE_URL + 'rate/<str:doctor_id>/')
        # patient = User.objects.get(id=5)
        # self.client.force_login(patient)
        pass

    def test_get_doctor_average_rate(self):
        pass

    def test_doctor_not_found(self):
        pass

    def test_not_integer_rate(self):
        pass

    def test_under_range_rate(self):
        pass

    def test_over_range_rate(self):
        pass

    def test_rate_submitted(self):
        pass

    def test_rate_saved(self):
        pass
