from django.urls import path
from .views import *

urlpatterns = [
    path('sign_up', SignUp.as_view(), name='SignUp')
]
