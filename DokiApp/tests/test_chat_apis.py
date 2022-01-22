from django.test import TestCase
from django.test import RequestFactory

from mixer.backend.django import mixer

from ..views import *
from ..models import *

LOCALHOST_BASE_URL = 'https://127.0.0.1:8000/api/'
MESSAGE_SET_5 = [
    {'id': 14, 'text': 'While all her friends were positive that Mary had a sixth sense.', 'seen': True,
     'is_sender_doctor': True},
    {'id': 15, 'text': 'He was all business when he wore his clown suit.', 'seen': True, 'is_sender_doctor': False},
    {'id': 10, 'text': 'I was fishing for compliments and accidentally caught a trout.', 'seen': True,
     'is_sender_doctor': True},
    {'id': 11, 'text': 'I love eating toasted cheese and tuna sandwiches.', 'seen': True, 'is_sender_doctor': True},
    {'id': 12, 'text': 'He decided to live his life by the big beats manifesto.', 'seen': True,
     'is_sender_doctor': False},
    {'id': 13, 'text': "If you don't like toenails, you probably shouldn't look at your feet.", 'seen': True,
     'is_sender_doctor': False},
    {'id': 7, 'text': 'He colored deep space a soft yellow.', 'seen': True, 'is_sender_doctor': False},
    {'id': 8, 'text': 'She finally understood that grief was her love with no place for it to go.', 'seen': True,
     'is_sender_doctor': False},
    {'id': 9, 'text': 'He was sure the Devil created red sparkly glitter.', 'seen': True, 'is_sender_doctor': True},
    {'id': 4, 'text': 'There was no telling what thoughts would come from the machine.', 'seen': True,
     'is_sender_doctor': False},
    {'id': 5, 'text': 'After exploring the abandoned building, he started to believe in ghosts.', 'seen': True,
     'is_sender_doctor': True},
    {'id': 6, 'text': "She wasn't sure whether to be impressed or concerned.", 'seen': True, 'is_sender_doctor': False},
    {'id': 1, 'text': 'When he asked her favorite number, she answered without hesitation that it was diamonds.',
     'seen': True, 'is_sender_doctor': False},
    {'id': 2, 'text': 'He knew it was going to be a bad day when he saw mountain lions roaming the streets.',
     'seen': True, 'is_sender_doctor': True},
    {'id': 3, 'text': 'The truth is that you pay for your lifestyle in hours.', 'seen': True, 'is_sender_doctor': False}
]


class TestChatList(TestCase):
    fixtures = ['doctors.json', 'doctor_profiles.json',
                'patients.json', 'patient_profiles.json',
                'reserves.json', 'chats.json']

    def test_not_authed(self):
        request = RequestFactory().get('api/chat_list', data={}, content_type='application/json')
        response = ChatList.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_no_chats_for_doctor(self):
        doctor = mixer.blend('DokiApp.User', is_doctor=True)
        self.client.force_login(doctor)
        response = self.client.get(LOCALHOST_BASE_URL + 'chat_list')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'chats': []})

    def test_no_chats_for_patient(self):
        patient = mixer.blend('DokiApp.User', is_doctor=False)
        self.client.force_login(patient)
        response = self.client.get(LOCALHOST_BASE_URL + 'chat_list')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'chats': []})

    def test_chats_for_doctor(self):
        doctor = User.objects.get(id=1)
        self.client.force_login(doctor)
        response = self.client.get(LOCALHOST_BASE_URL + 'chat_list')

        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'chats': [
            {'doctor': 1, 'patient': 1, 'partner_username': 'patient_1',
             'partner_picture_url': 'default.png', 'has_new_message': False},
            {'doctor': 1, 'patient': 2, 'partner_username': 'patient_2',
             'partner_picture_url': None, 'has_new_message': False},
            {'doctor': 1, 'patient': 3, 'partner_username': 'patient_3',
             'partner_picture_url': None, 'has_new_message': False}]}
        self.assertEqual(response.data, response_result)

    def test_chats_for_patient(self):
        patient = User.objects.get(id=6)
        self.client.force_login(patient)
        response = self.client.get(LOCALHOST_BASE_URL + 'chat_list')

        self.assertEqual(response.status_code, 200)
        response_result = {'success': True, 'chats': [
            {'doctor': 1, 'patient': 2, 'partner_username': 'DRE',
             'partner_picture_url': 'default.png', 'has_new_message': False},
            {'doctor': 2, 'patient': 2, 'partner_username': 'CJ',
             'partner_picture_url': None, 'has_new_message': False}]}
        self.assertEqual(response.data, response_result)


class TestLoadOldChat(TestCase):
    fixtures = ['doctors.json', 'doctor_profiles.json',
                'patients.json', 'patient_profiles.json',
                'reserves.json', 'chats.json', 'messages.json']

    def test_not_authed(self):
        request = RequestFactory().get('api/load_old_chat', data={}, content_type='application/json')
        response = LoadOldChat.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_partner_does_not_exist(self):
        doctor = User.objects.get(id=1)
        self.client.force_login(doctor)
        data = {'partner_username': 'spam'}
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)

        self.assertEqual(response.status_code, 404)

    def test_chat_does_not_exist(self):
        doctor = User.objects.get(id=1)
        self.client.force_login(doctor)
        data = {'partner_username': 'patient_4'}
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)

        self.assertEqual(response.status_code, 404)

    def test_there_is_no_message(self):
        doctor = User.objects.get(id=1)
        self.client.force_login(doctor)
        data = {'partner_username': 'patient_1'}
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'messages': [], 'oldest_unseen_message_id': 0})

    def test_all_messages_are_seen(self):
        for message in Message.objects.all():
            message.set_as_seen()

        doctor = User.objects.get(id=2)
        self.client.force_login(doctor)
        data = {'partner_username': 'patient_1'}
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['messages']), 15)
        self.assertEqual(response.data['oldest_unseen_message_id'], 0)

        r = []
        for m in response.data['messages']:
            m.pop('date')
            r.append(m)
        for message in r:
            self.assertTrue(message in MESSAGE_SET_5)

    def test_oldest_unseen_message(self):
        doctor = User.objects.get(id=2)
        self.client.force_login(doctor)
        data = {'partner_username': 'patient_1'}
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(len(response.data['messages']), 15)
        self.assertEqual(response.data['oldest_unseen_message_id'], 6)

    def test_patient_messages_set_as_seen(self):
        doctor = User.objects.get(id=2)
        self.client.force_login(doctor)
        data = {'partner_username': 'patient_1'}
        self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        self.assertEqual(response.status_code, 200)

        for message in response.data['messages']:
            if not message['is_sender_doctor']:
                self.assertTrue(message['seen'])

    def test_doctor_messages_set_as_seen(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'partner_username': 'CJ'}
        self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        self.assertEqual(response.status_code, 200)

        for message in response.data['messages']:
            if message['is_sender_doctor']:
                self.assertTrue(message['seen'])

    def test_user_messages_not_set_as_seen_for_doctor(self):
        doctor = User.objects.get(id=2)
        self.client.force_login(doctor)
        data = {'partner_username': 'patient_1'}
        self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        self.assertEqual(response.status_code, 200)

        for message in response.data['messages']:
            if message['is_sender_doctor']:
                self.assertFalse(message['seen'])

    def test_user_messages_not_set_as_seen_for_patient(self):
        patient = User.objects.get(id=5)
        self.client.force_login(patient)
        data = {'partner_username': 'CJ'}
        self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        response = self.client.get(LOCALHOST_BASE_URL + 'load_old_chat', data)
        self.assertEqual(response.status_code, 200)

        for message in response.data['messages']:
            if not message['is_sender_doctor']:
                self.assertFalse(message['seen'])
