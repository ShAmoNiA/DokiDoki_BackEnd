from ..models import User
from ..serializers import UserSerializer, CommentSerializer, MessageSerializer, ChatSerializer


class ProfileAdapter:
    def adapt_profile(self, user):
        if user.is_doctor:
            profile = self.adapt_doctor_profile(user)
        else:
            profile = self.adapt_patient_profile(user)
        return profile

    def adapt_doctor_profile(self, user):
        user_serializer = UserSerializer(instance=user)
        profile = user.profile

        data = user_serializer.data
        data.pop('password')

        data["degree"] = profile.degree
        data["medical_degree_photo"] = profile.medical_degree_photo
        data["cv"] = profile.cv
        data["office_location"] = profile.office_location
        data["expertise_tags"] = profile.expertise_tags
        data["rate"] = profile.rate
        data["comments_count"] = profile.comments_count

        return data

    def adapt_patient_profile(self, user):
        user_serializer = UserSerializer(instance=user)
        profile = user.profile

        data = user_serializer.data
        data.pop('password')

        data["weight"] = profile.weight
        data["height"] = profile.height
        data["medical_records"] = profile.medical_records
        return data


def adapt_profile_queryset_to_list(profiles):
    users = []
    for profile in profiles:
        users.append(profile.user)

    return adapt_user_queryset_to_dict(users)


def adapt_user_queryset_to_dict(users):
    result = {}
    for user in users:
        result[user.id] = ProfileAdapter().adapt_profile(user)
    return result


def adapt_user_queryset_to_list(users):
    result = []
    for user in users:
        data = ProfileAdapter().adapt_profile(user)
        data['id'] = user.id
        result.append(data)
    return result


def adapt_comment(comments):
    result = []
    for comment in comments:
        data = CommentSerializer(instance=comment).data
        data["writer_name"] = User.objects.get(id=data['writer']).username
        result.append(data)
    return result


def adapt_chat(chats, user):
    result = []
    for chat in chats:
        data = ChatSerializer(instance=chat).data

        data['partner_username'] = chat.get_partner_user(user).username
        data['partner_picture_url'] = chat.get_partner_user(user).profile_picture_url
        data['has_new_message'] = chat.has_new_message(user)

        result.append(data)
    return result


def adapt_message(messages):
    result = []
    for message in messages:
        data = MessageSerializer(instance=message).data
        result.append(data)
    return result
