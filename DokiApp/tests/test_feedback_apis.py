from django.test import TestCase

from mixer.backend.django import mixer

from django.utils.datastructures import MultiValueDictKeyError

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'


class TestWriteComment(TestCase):
    fixtures = ['doctors.json', 'doctor_profiles.json', 'patients.json']

    def test_not_authed(self):
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment')
        self.assertEqual(response.status_code, 401)

    def test_text_not_passed(self):
        patient = User.objects.get(id=5)
        data = {'doctor_id': 3}
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'success': False, 'message': 'Comment is empty'})

    def test_text_is_empty(self):
        patient = User.objects.get(id=5)
        data = {'text': "", 'doctor_id': 3}
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'success': False, 'message': 'Comment is empty'})

    def test_text_is_space(self):
        patient = User.objects.get(id=5)
        data = {'text': " ", 'doctor_id': 3}
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'success': False, 'message': 'Comment is empty'})

    def test_doctor_profile_not_found(self):
        patient = User.objects.get(id=5)
        data = {'text': "ok", 'doctor_id': 6}
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'success': False, 'message': 'Doctor not found'})

    def test_doctor_user_not_found(self):
        patient = User.objects.get(id=5)
        data = {'text': "ok", 'doctor_id': 11}
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        self.assertEqual(response.status_code, 404)

    def test_comment_wrote(self):
        patient = User.objects.get(id=5)
        data = {'text': "ok", 'doctor_id': 3}
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Comment submitted'})

    def test_comment_saved(self):
        patient = User.objects.get(id=5)
        data = {'text': "ok", 'doctor_id': 3}
        self.client.force_login(patient)
        self.client.post(LOCALHOST_BASE_URL + 'new_comment', data)

        comment = Comment.objects.get(id=1)
        self.assertEqual(comment.writer, patient)
        self.assertEqual(comment.doctor, DoctorProfile.objects.get(id=3))
        self.assertEqual(comment.text, 'ok')


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
    fixtures = ['doctors.json', 'doctor_profiles.json', 'patients.json', 'rates.json']

    def test_get_not_authed(self):
        response = self.client.get(LOCALHOST_BASE_URL + 'rate/2/')
        self.assertEqual(response.status_code, 401)

    def test_get_doctor_average_rate(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.get(LOCALHOST_BASE_URL + 'rate/3/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'rate': 4})

    def test_get_doctor_not_found(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.get(LOCALHOST_BASE_URL + 'rate/9/')

        self.assertEqual(response.status_code, 404)

    def test_get_not_integer_rate(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.get(LOCALHOST_BASE_URL + 'rate/2/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'rate': 10/3})

    def test_post_not_authed(self):
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/')
        self.assertEqual(response.status_code, 401)

    def test_post_rate_not_passed(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        with self.assertRaises(Exception) as raised:
            self.client.post(LOCALHOST_BASE_URL + 'rate/2/')
        self.assertEqual(MultiValueDictKeyError, type(raised.exception))

    def test_post_doctor_not_found(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/9/', {'rate': 3})

        self.assertEqual(response.status_code, 404)

    def test_post_not_integer_rate(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 3.2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Rate submitted!'})
        self.assertEqual(Rate.objects.all()[::-1][0].rate, 3)

    def test_under_range_rate_between_0_1(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 0.6})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message']['rate'][0], 'Enter rate between 1 and 5')

    def test_under_range_rate_zero(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 0})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message']['rate'][0], 'Enter rate between 1 and 5')

    def test_under_range_rate_negative(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': -1})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message']['rate'][0], '"-1" is not a valid choice.')

    def test_over_range_rate(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 6})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message']['rate'][0], '"6" is not a valid choice.')

    def test_rate_submitted_integer(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 3})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Rate submitted!'})

    def test_rate_submitted_float(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 3.2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Rate submitted!'})

    def test_rate_saved_integer(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 3})

        self.assertEqual(Rate.objects.all()[::-1][0].rate, 3)

    def test_rate_saved_float(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        self.client.post(LOCALHOST_BASE_URL + 'rate/2/', {'rate': 3.2})

        self.assertEqual(Rate.objects.all()[::-1][0].rate, 3)
