from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from ..models import *
from ..helper_functions import *
from ..serializers import *


class ProfilePreview(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        profile = self.get_adapted_profile(user)
        return Response({"success": True, "profile": profile}, status=status.HTTP_200_OK)

    def get_adapted_profile(self, user):
        if user.is_doctor:
            profile = doctor_profile_adapter(user)
        else:
            profile = patient_profile_adapter(user)
        return profile


@api_view(['POST'])
def edit_profile(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"success": False, "message": "You must login first"}, status=status.HTTP_200_OK)
    profile = user.get_profile()

    data = pop_dangerous_keys(request)
    serializerClass = get_profile_serializer(user)

    serializer = serializerClass(profile, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    serializer = UserSerializer(user, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"success": True, "message": "Profile changed successfully"}, status=status.HTTP_200_OK)
