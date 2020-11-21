from rest_framework import serializers

from . import models


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Users
        fields = ('user_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
