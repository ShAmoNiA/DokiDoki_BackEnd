from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token
from .views import *


EMAIL_TOKEN = 'c754wcRr0f7c4cweFEqxgtDv5409wAw420erOmcDft43mDcr9PlFD'

urlpatterns = [
    path('send_email/' + EMAIL_TOKEN, send_email_by_front, name='send_email_by_front'),
]

auth_urls = [
    path('sign_up', SignUp.as_view(), name='SignUp'),
    path('login', LogIn.as_view(), name="LogIn"),
    path('logout', LogOut.as_view(), name='LogOut'),

    path('check_username/<str:username>', CheckUsername.as_view(), name='CheckUsername'),

    path('verify_email', VerifyEmail.as_view(), name='VerifyEmail'),
    path('forgot_password', forgot_password, name='forgot_password'),
    path('reset_password', ResetPassword.as_view(), name='ResetPassword'),
]

pack_list = [
    auth_urls,
]


for pack in pack_list:
    for url in pack:
        urlpatterns.append(url)
