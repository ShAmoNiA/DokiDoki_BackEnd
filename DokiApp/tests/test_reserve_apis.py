from django.test import TestCase
from django.test import RequestFactory

from mixer.backend.django import mixer

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'


class TestReserveDoctor(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json']

    def test_not_authed(self):
        request = RequestFactory().post('api/reserve', data={}, content_type='application/json')
        response = ReserveDoctor.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_not_patient(self):
        doctor = mixer.blend('DokiApp.User', is_doctor=True)
        self.client.force_login(doctor)
        response = self.client.post(LOCALHOST_BASE_URL + 'reserve')

        self.assertEqual(response.status_code, 403)

    def test_doctor_not_found(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'time': 'AM', 'date': '2017-07-23', 'doctor_id': 9}
        response = self.client.post(LOCALHOST_BASE_URL + 'reserve', data)

        self.assertEqual(response.status_code, 404)

    def test_reserving_a_patient(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'time': 'AM', 'date': '2017-07-23', 'doctor_id': 6}
        response = self.client.post(LOCALHOST_BASE_URL + 'reserve', data)

        self.assertEqual(response.status_code, 404)

    def test_reserved(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'time': 'AM', 'date': '2017-07-23', 'doctor_id': 3}
        response = self.client.post(LOCALHOST_BASE_URL + 'reserve', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Reserved!'})

    def test_reserve_object_saved(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'time': 'AM', 'date': '2017-07-23', 'doctor_id': 3}
        self.client.post(LOCALHOST_BASE_URL + 'reserve', data)

        reserve = Reserve.objects.get(id=1)
        self.assertEqual(reserve.doctor, DoctorProfile.objects.get(id=3))
        self.assertEqual(reserve.creator, patient)
        self.assertEqual(reserve.time, 'AM')
        self.assertEqual(str(reserve.date), '2017-07-23')

    def test_chat_object_saved(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'time': 'AM', 'date': '2017-07-23', 'doctor_id': 3}
        self.client.post(LOCALHOST_BASE_URL + 'reserve', data)

        chat = Chat.objects.get(id=1)
        self.assertEqual(chat.doctor, DoctorProfile.objects.get(id=3))
        self.assertEqual(chat.patient, patient.profile)
        self.assertEqual(chat.name, 'chat_3_5')


class TestReserveList(TestCase):
    fixtures = ['patients.json', 'patient_profiles.json',
                'doctors.json', 'doctor_profiles.json', 'reserves.json']

    def test_not_authed(self):
        request = RequestFactory().post('api/reserves', data={}, content_type='application/json')
        response = ReserveList.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_not_doctor(self):
        patient = mixer.blend('DokiApp.User', is_doctor=False)
        self.client.force_login(patient)
        response = self.client.post(LOCALHOST_BASE_URL + 'reserves')

        self.assertEqual(response.status_code, 403)

    def test_no_reserves(self):
        doctor = mixer.blend('DokiApp.User', is_doctor=True)
        self.client.force_login(doctor)
        response = self.client.get(LOCALHOST_BASE_URL + 'reserves')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'reserves': []})

    def test_reserves_showed(self):
        doctor = DoctorProfile.objects.get(id=1).user
        self.client.force_login(doctor)
        response = self.client.get(LOCALHOST_BASE_URL + 'reserves')

        response_result = {'success': True, 'reserves': [
            {"doctor": 1, "creator": 5, "date": "2012-09-06", "time": "AM"},
            {"doctor": 1, "creator": 6, "date": "2022-01-01", "time": "PM"},
            {"doctor": 1, "creator": 7, "date": "2017-09-23", "time": "AM"}]}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, response_result)
