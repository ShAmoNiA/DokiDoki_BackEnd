from django.test import TestCase
from mixer.backend.django import Mixer

from django.db import IntegrityError

from ..models import *


class NeutralMixer(Mixer):
    def blend(self, scheme, **values):

        type_mixer = self.get_typemixer(scheme)
        try:
            return type_mixer.blend(**values)
        except Exception as e:
            if self.params.get('silence'):
                return None
            if e.args:
                e.args = ('Mixer (%s): %s' % (scheme, e.args[0]),) + e.args[1:]
                # The line below is deleted, so errors won't be logged in commandline
                # LOGGER.error(traceback.format_exc())
            raise


mixer = NeutralMixer()


class TestUser(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.User')
        self.assertEqual(obj.pk, 1)

    def test_fields(self):
        obj = mixer.blend('DokiApp.User', username="username_1", email="email@email.com", phone="09371112233",
                          fullname="full name 1", verify_email_token="6843gt43hfr")
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.username, "username_1")
        self.assertEqual(obj.email, "email@email.com")
        self.assertEqual(obj.phone, "09371112233")
        self.assertEqual(obj.fullname, "full name 1")
        self.assertEqual(obj.verify_email_token, "6843gt43hfr")
        self.assertEqual(obj.reset_password_token, "expired")

    def test_duplicated_username(self):
        mixer.blend("DokiApp.User", username="username_1")
        with self.assertRaises(Exception) as raised:
            mixer.blend("DokiApp.User", username="username_1")
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_duplicated_email(self):
        mixer.blend("DokiApp.User", email="email@email.com")
        with self.assertRaises(Exception) as raised:
            mixer.blend("DokiApp.User", email="email@email.com")
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_duplicated_phone(self):
        mixer.blend("DokiApp.User", phone="09371112233")
        with self.assertRaises(Exception) as raised:
            mixer.blend("DokiApp.User", phone="09371112233")
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_verified_email(self):
        obj_1 = mixer.blend('DokiApp.User', verify_email_token="6843gt43hfr")
        obj_2 = mixer.blend('DokiApp.User', verify_email_token="")
        obj_3 = mixer.blend('DokiApp.User', verify_email_token="verifin")
        self.assertFalse(obj_1.verified_email)
        self.assertFalse(obj_2.verified_email)
        self.assertFalse(obj_3.verified_email)

    def test_verify_email(self):
        obj_1 = mixer.blend('DokiApp.User', verify_email_token="verified")
        self.assertTrue(obj_1.verified_email)

        obj_2 = mixer.blend('DokiApp.User', verify_email_token="ewb")
        obj_2.verify_email()
        self.assertTrue(obj_2.verified_email)


class TestDoctorProfile(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.DoctorProfile')
        self.assertEqual(obj.pk, 1)


class TestPatientProfile(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.DoctorProfile')
        self.assertEqual(obj.pk, 1)


class TestImage(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.Image')
        self.assertEqual(obj.pk, 1)
