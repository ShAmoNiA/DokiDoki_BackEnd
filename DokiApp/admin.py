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
class CommentAdmin(admin.ModelAdmin):
    list_display = ['writer', 'doctor', 'text']
    list_filter = ['writer', 'doctor', 'date']
    list_editable = ['text']


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'rate']
    list_filter = ['user', 'doctor', 'rate']
    list_editable = ['rate']


@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'creator', 'date', 'time']
    # TODO: list_filter, list_editable


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor', 'patient']
    list_filter = ['doctor', 'patient']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text', 'seen', 'chat', 'is_sender_doctor', 'date']
    list_filter = ['chat', 'seen']
