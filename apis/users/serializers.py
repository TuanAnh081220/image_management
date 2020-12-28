from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from .models import Users, PendingUsers


class GetAllDetailedUserSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'user_name', 'email', 'is_admin', 'is_blocked', 'last_login')


class DetailedUserSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_name', 'email', 'password', 'avatar', 'last_login')


class PendingUserSerializer(ModelSerializer):
    class Meta:
        model = PendingUsers
        fields = '__all__'


class UpdateDetailedUserSerializer(Serializer):
    user_name = serializers.CharField(max_length=45)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=45)

    def update(self, instance, validated_data):
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.password = validated_data.get('password', instance.password)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
