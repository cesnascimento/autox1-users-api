from rest_framework import serializers
from .models import CustomUser, Roles, UserActivities, TokenWPP, WPPGroup


class TokenWPPSerializer(serializers.Serializer):
    token_wpp = serializers.CharField()
    class Meta:
        model = TokenWPP
        fields = "__all__"


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField()
    role = serializers.ChoiceField(Roles)
    token = TokenWPPSerializer(read_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(required=False)
    is_new_user = serializers.BooleanField(default=False, required=False)


class UpdatePasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):

    token = TokenWPPSerializer()

    class Meta:
        model = CustomUser
        exclude = ("password", )


class UserActivitiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivities
        fields = ("__all__")


class WPPGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = WPPGroup
        fields = ['origin', 'invite_link']