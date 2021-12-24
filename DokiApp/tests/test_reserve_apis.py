from django.test import TestCase

from mixer.backend.django import mixer

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'


class TestReserveDoctor(TestCase):

    def test_not_authed(self):
        pass

    def test_not_patient(self):
        pass

    def test_doctor_not_found(self):
        pass

    def test_reserved(self):
        pass

    def test_reserve_saved(self):
        pass


class TestReserveList(TestCase):

    def test_not_authed(self):
        pass

    def test_not_doctor(self):
        pass

    def test_no_reserves(self):
        pass

    def test_reserves_showed(self):
        pass
