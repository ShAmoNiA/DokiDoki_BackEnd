from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from .views import *

EMAIL_TOKEN = 'c754wcRr0f7c4cweFEqxgtDv5409wAw420erOmcDft43mDcr9PlFD'

urlpatterns = [
    path('send_email' + EMAIL_TOKEN, SendEmail.as_view(), name='SendEmail'),
]

auth_urls = [
    path('sign_up', SignUp.as_view(), name='SignUp'),
    path('login', LogIn.as_view(), name="LogIn"),
    path('logout', LogOut.as_view(), name='LogOut'),

    path('check_username/<str:username>/', CheckUsername.as_view(), name='CheckUsername'),

    path('verify_email', VerifyEmail.as_view(), name='VerifyEmail'),
    path('forgot_password', ForgotPassword.as_view(), name='ForgotPassword'),
    path('reset_password', ResetPassword.as_view(), name='ResetPassword'),
]

profile_urls = [
    path('upload_image', UploadImage.as_view(), name='UploadImage'),

    path('profile_preview', ProfilePreview.as_view(), name='ProfilePreview'),
    path('my_profile_preview', MyProfilePreview.as_view(), name='MyProfilePreview'),

    path('edit_profile', EditProfile.as_view(), name='EditProfile'),
    path('add_expertise', AddExpertise.as_view(), name='AddExpertise'),
]

search_urls = [
    path('all_tags', AllTags.as_view(), name='AllTags'),
    path('search_doctor_by_name', SearchDoctorByName.as_view(), name='SearchDoctorByName'),
    path('search_doctor_by_tag', SearchDoctorByTag.as_view(), name='SearchDoctorByTag'),

    path('search/<str:keyword>/', SearchDoctorByKeyword.as_view(), name='SearchDoctorByKeyword'),
    path('tags/<str:keyword>/', SearchDoctorsWithTag.as_view(), name='SearchDoctorsWithTag'),
    path('search/', AdvancedSearch.as_view(), name="AdvancedSearch"),
]

feedback_urls = [
    path('new_comment', WriteComment.as_view(), name="WriteComment"),
    path('comments/<str:doctor_id>/', GetComments.as_view(), name="GetComments"),
    path('rate/<str:doctor_id>/', RateDoctor.as_view(), name="RateDoctor"),
]

reserve_urls = [
    path('reserve', ReserveDoctor.as_view(), name='ReserveDoctor'),
    path('reserves', ReserveList.as_view(), name='ReserveList'),
]

chat_urls = [
    path('load_old_chat', LoadOldChat.as_view(), name='load_old_chat'),
    path('chat_list', ChatList.as_view(), name='chat_list'),
]

pack_list = [
    auth_urls,
    profile_urls,
    search_urls,
    feedback_urls,
    reserve_urls,
    chat_urls,
]

for pack in pack_list:
    for url in pack:
        urlpatterns.append(url)
