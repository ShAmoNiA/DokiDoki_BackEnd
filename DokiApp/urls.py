from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token
from .views import *


EMAIL_TOKEN = 'c754wcRr0f7c4cweFEqxgtDv5409wAw420erOmcDft43mDcr9PlFD'

urlpatterns = [
    path('send_email' + EMAIL_TOKEN, send_email_by_front, name='send_email_by_front'),
]

auth_urls = [
    path('sign_up', SignUp.as_view(), name='SignUp'),
    path('login', LogIn.as_view(), name="LogIn"),
    path('logout', LogOut.as_view(), name='LogOut'),

    path('check_username/<str:username>/', CheckUsername.as_view(), name='CheckUsername'),

    path('verify_email', VerifyEmail.as_view(), name='VerifyEmail'),
    path('forgot_password', forgot_password, name='forgot_password'),
    path('reset_password', ResetPassword.as_view(), name='ResetPassword'),
]

profile_urls = [
    path('edit_profile', edit_profile),
    path('upload_image', ImageView.as_view(), name='UploadImage'),
    path('add_tag', AddTag.as_view(), name='AddTag'),
    path('search_by_tag', SearchForTag.as_view(), name='SearchForTag'),
    path('search_doctor_by_name', SearchDoctorByName.as_view(), name='SearchDoctorByName'),
    path('search_doctor_by_tag', SearchDoctorByTag.as_view(), name='SearchDoctorByTag'),

    path('preview_doctor_profile', PreviewDoctorProfile.as_view(), name='PreviewDoctorProfile'),
    path('preview_patient_profile', PreviewPatientProfile.as_view(), name='PreviewPatientProfile'),
]

pack_list = [
    auth_urls,
    profile_urls
]


for pack in pack_list:
    for url in pack:
        urlpatterns.append(url)
