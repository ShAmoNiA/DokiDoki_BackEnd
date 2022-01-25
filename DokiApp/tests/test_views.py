from django.test import TestCase
from django.test import RequestFactory
from django.test.client import encode_multipart

from mixer.backend.django import mixer

from django.contrib.auth import authenticate

from ..views import *
from ..models import *


LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'


class TestSendEmail(TestCase):

    def test_send(self):
        EMAIL = "ntm.patronage@gmail.com"
        data = {"subject": "the_subject",
                "message": "the_message",
                "to_list": EMAIL}
        request = RequestFactory().post('api/send_email', data, content_type='application/json')
        response = SendEmail.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'message': 'email sent'}
        self.assertEqual(response.data, response_result)


class TestUploadImage(TestCase):

    @staticmethod
    def generate_photo_file():
        import os
        import io
        from PIL import Image as ImageCreator

        file = io.BytesIO()
        image = ImageCreator.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_upload_image(self):
        # TODO: fix this function
        photo_file = self.generate_photo_file()
        data = {'image': photo_file}

        request = RequestFactory().post('api/upload_image', data,
                                        content_type='multipart/form-data; boundary=<calculated when request is sent>')
        response = UploadImage.as_view()(request)

        self.assertEqual(response.status_code, 200)
        response_result = {"image_url": "/images/default.png"}
        self.assertEqual(response.data, response_result)

    def test_upload_image_default(self):
        request = RequestFactory().post('api/upload_image',
                                        content_type='multipart/form-data; boundary=<calculated when request is sent>')
        response = UploadImage.as_view()(request)

        self.assertEqual(response.status_code, 200)
        response_result = {"image_url": "/images/default.png"}
        self.assertEqual(response.data, response_result)
