from django.test import TestCase

from mixer.backend.django import mixer

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'


class TestWriteComment(TestCase):

    def test_not_authed(self):
        pass

    def test_text_is_empty(self):
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

    def test_no_comments(self):
        pass

    def test_comments_showed(self):
        pass


class TestRateDoctor(TestCase):

    def test_not_authed(self):
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
