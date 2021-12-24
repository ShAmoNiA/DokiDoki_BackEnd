import os
from shutil import copyfile as copy

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import encode_multipart

from mixer.backend.django import mixer

from django.contrib.auth import authenticate

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'

class TestComment(TestCase):
    def test_read_comments(self):
        # self.client.force_login(User.objects.get(id=1))
        cm = Comment()