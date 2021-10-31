from django.conf.urls import url
from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token
from .views import *


EMAIL_TOKEN = 'c754wcnr0f7c4cwefm-qxgtvv5409wxw,^#4-2!0*erpmcwef#$t43mumc##r$,9PCFD'

urlpatterns = [
    path('sign_up', SignUp.as_view(), name='SignUp'),
    url('^check_username/(?P<username>.+)/$', view=CheckUsername.as_view(), name='CheckUsername'),
    path('login', LogIn.as_view(), name="LogIn"),
    path('logout', LogOut.as_view(), name='LogOut'),
    path('verify_email', VerifyEmail.as_view(), name='VerifyEmail'),
    path('forgot_password', forgot_password, name='forgot_password'),
    path('reset_password', ResetPassword.as_view(), name='ResetPassword'),

    path('send_email/' + EMAIL_TOKEN, send_email_by_front, name='send_email_by_front'),
]
