from django.contrib import admin
from .models import *


admin.site.register(Image)
admin.site.register(User)
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
