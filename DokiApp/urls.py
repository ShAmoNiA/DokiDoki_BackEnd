from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    path('sign_up', SignUp.as_view(), name='SignUp'),
    path('login', LogIn.as_view(), name="LogIn"),
    path('logout', LogOut.as_view(), name='LogOut'),
]
