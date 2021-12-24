from django.contrib import admin
from .models import *


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'verify_email_token', 'is_doctor', 'fullname']
    list_editable = ['verify_email_token']
    list_filter = ['is_doctor', 'verify_email_token']
    search_fields = ['username', 'email']

    actions = ['verify_email']

    def verify_email(self, request, queryset):
        for user in queryset:
            user.verify_email()


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'degree', 'cv', 'office_location']
    list_filter = ['degree', 'office_location']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'medical_records']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title']
    list_filter = ['title']


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'tag', 'image_url']
    list_filter = ['doctor', 'tag']

@admin.register(Comment)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['writer', 'doctor', 'text']

@admin.register(Rate)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'rate']

@admin.register(Reserve)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'user', 'date', 'time']

