from django.db.models import QuerySet
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class TestRegister(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("register")

    def test_invalid_username_register(self):
        data = {
            "username": "DL$",
            "email": "validemail@email.com",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)
        user:QuerySet = User.objects.filter(username="DL$")
        self.assertEquals(user.count(),0)



    def test_duplicate_username_register(self):
        data = {
            "username": "DL",
            "email": "validemail@email.com",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        data = {
            "username": "DL",
            "email": "Another@email.com",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 400)

    def test_invalid_email_register(self):
        for email in ["InvalidEmail.com", "invalid@email", "@.", "!!@%%.$@"]:
            data = {
                "username": "DL",
                "email": email,
                "password": "password"
            }
            response = self.client.post(self.url, data)
            self.assertEquals(response.status_code, 400)
            user: QuerySet = User.objects.filter()
            self.assertEquals(user.count(), 0)

    def test_duplicate_email_register(self):
        data = {
            "username": "DL",
            "email": "validemail@email.com",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        data = {
            "username": "Mamad",
            "email": "validemail@email.com",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertNotEquals(response.status_code, 200)

    def test_invalid_password_register(self):
        for password in ["P:1", "passwordddd", "5843574387598.","Password123456", "!!@%%.$%$#@"]:
            data = {
                "username": "DL",
                "email": "email@email.com",
                "password": password
            }
            response = self.client.post(self.url, data)
            self.assertEquals(response.status_code, 400)
            user: QuerySet = User.objects.filter()
            self.assertEquals(user.count(), 0)
