from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apis.users.models import Users, PendingUsers


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_admin'] = user.is_admin
        return token
