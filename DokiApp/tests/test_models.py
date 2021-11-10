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
                          fullname="full name 1", verify_email_token="6843gt43hfr", profile_picture_url="image_url",
                          first_name="fn", lsat_name="ln")
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.username, "username_1")
        self.assertEqual(obj.profile_picture_url, "image_url")
        self.assertEqual(obj.first_name, "fn")
        self.assertEqual(obj.lsat_name, "ln")
        self.assertEqual(obj.sex, "P")
        self.assertEqual(obj.email, "email@email.com")
        self.assertEqual(obj.phone, "09371112233")
        self.assertEqual(obj.fullname, "full name 1")
        self.assertEqual(obj.verify_email_token, "6843gt43hfr")
        self.assertEqual(obj.reset_password_token, "expired")

        obj = mixer.blend('DokiApp.User', sex="M")
        self.assertEqual(obj.pk, 2)
        self.assertEqual(obj.sex, "M")

    def test_properties(self):
        obj = mixer.blend('DokiApp.User')
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.profile, None)
        self.assertEqual(obj.has_profile, False)
        self.assertEqual(obj.verified_email, False)
        self.assertEqual(obj.is_patient, True)

    def test_has_profile(self):
        obj = mixer.blend('DokiApp.User')
        mixer.blend('DokiApp.PatientProfile', user=obj)
        obj = User.objects.get(id=1)
        self.assertEqual(obj.has_profile, True)

        obj = mixer.blend('DokiApp.User')
        mixer.blend('DokiApp.DoctorProfile', user=obj)
        obj = User.objects.get(id=2)
        self.assertEqual(obj.has_profile, False)

    def test_profile_doctor(self):
        user = mixer.blend('DokiApp.User', is_doctor=True)
        profile = mixer.blend('DokiApp.DoctorProfile', user=user)
        user = User.objects.get(id=1)
        self.assertEqual(user.profile, profile)
        self.assertTrue(user.has_profile)

    def test_profile_patient(self):
        user = mixer.blend('DokiApp.User', is_doctor=False)
        profile = mixer.blend('DokiApp.PatientProfile', user=user)
        user = User.objects.get(id=1)
        self.assertEqual(user.profile, profile)
        self.assertTrue(user.has_profile)

    def test_sex_choices(self):
        obj = mixer.blend('DokiApp.User')
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.sex, "P")

        obj = mixer.blend('DokiApp.User', sex="M")
        self.assertEqual(obj.pk, 2)
        self.assertEqual(obj.sex, "M")

        obj = mixer.blend('DokiApp.User', sex="F")
        self.assertEqual(obj.pk, 3)
        self.assertEqual(obj.sex, "F")

        obj = mixer.blend('DokiApp.User', sex="U")
        self.assertEqual(obj.pk, 4)
        self.assertEqual(obj.sex, "U")

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

    def test_fields(self):
        obj = mixer.blend('DokiApp.DoctorProfile', user=None, medical_degree_photo=None, office_location=None)
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.user, None)
        self.assertEqual(obj.degree, "general")
        self.assertEqual(obj.medical_degree_photo, None)
        self.assertEqual(obj.cv, "default")
        self.assertEqual(obj.office_location, None)

        obj = mixer.blend('DokiApp.DoctorProfile', degree="the degree", user=None,
                          medical_degree_photo="photo", office_location="location")
        self.assertEqual(obj.pk, 2)
        self.assertEqual(obj.user, None)
        self.assertEqual(obj.degree, "the degree")
        self.assertEqual(obj.medical_degree_photo, "photo")
        self.assertEqual(obj.cv, "default")
        self.assertEqual(obj.office_location, "location")

    def test_set_user(self):
        obj = mixer.blend('DokiApp.DoctorProfile', user=None)
        self.assertEqual(obj.user, None)

        user_patient = mixer.blend('DokiApp.User', is_doctor=False)
        user_doctor = mixer.blend('DokiApp.User', is_doctor=True)
        set_1 = obj.set_user(user_patient)
        set_2 = obj.set_user(user_doctor)
        self.assertEqual(set_1, "The user is a patient")
        self.assertEqual(set_2, "the profile set successfully")
        profile = DoctorProfile.objects.get(id=1)
        self.assertEqual(User.objects.get(id=2).profile, profile)
        self.assertEqual(profile.user, User.objects.get(id=2))

        profile = DoctorProfile.objects.get(id=1)
        user_doctor = User.objects.get(id=2)
        user_patient = User.objects.get(id=1)
        set_3 = profile.set_user(user_doctor)
        set_4 = profile.set_user(user_patient)
        self.assertEqual(set_3, "The user already has a profile")
        self.assertEqual(set_4, "The user is a patient")


class TestPatientProfile(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.PatientProfile')
        self.assertEqual(obj.pk, 1)

    def test_fields(self):
        obj = mixer.blend('DokiApp.PatientProfile', medical_records=None, user=None)
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.user, None)
        self.assertEqual(obj.weight, 0)
        self.assertEqual(obj.height, 0)
        self.assertEqual(obj.medical_records, None)

        obj = mixer.blend('DokiApp.PatientProfile', weight=76, height=173,
                          medical_records="the records", user=None)
        self.assertEqual(obj.pk, 2)
        self.assertEqual(obj.user, None)
        self.assertEqual(obj.weight, 76)
        self.assertEqual(obj.height, 173)
        self.assertEqual(obj.medical_records, "the records")

    def test_set_user(self):
        obj = mixer.blend('DokiApp.PatientProfile', user=None)
        self.assertEqual(obj.user, None)

        user_patient = mixer.blend('DokiApp.User', is_doctor=False)
        user_doctor = mixer.blend('DokiApp.User', is_doctor=True)
        set_1 = obj.set_user(user_doctor)
        set_2 = obj.set_user(user_patient)
        self.assertEqual(set_1, "The user is a doctor")
        self.assertEqual(set_2, "the profile set successfully")
        profile = PatientProfile.objects.get(id=1)
        self.assertEqual(User.objects.get(id=1).profile, profile)
        self.assertEqual(profile.user, User.objects.get(id=1))

        profile = PatientProfile.objects.get(id=1)
        user_doctor = User.objects.get(id=2)
        user_patient = User.objects.get(id=1)
        set_3 = profile.set_user(user_doctor)
        set_4 = profile.set_user(user_patient)
        self.assertEqual(set_3, "The user is a doctor")
        self.assertEqual(set_4, "The user already has a profile")


class TestImage(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.Image')
        self.assertEqual(obj.pk, 1)

    def test_fields(self):
        obj = mixer.blend('DokiApp.Image', image="default.png")
        self.assertEqual(obj.pk, 1)
        self.assertEqual(obj.image, "default.png")


class TestTag(TestCase):

    def test_create(self):
        obj = mixer.blend('DokiApp.Tag')
        self.assertEqual(obj.pk, 1)
        
        obj = mixer.blend('DokiApp.tag', title="the title")
        self.assertEqual(obj.pk, 2)
        self.assertEqual(obj.title, "the title")
