from rest_framework import serializers
from .models import Tags, Images_Tags

class GetAllTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'created_at', 'updated_at')

class TagCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=45)

class ImageTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images_Tags
        fields = ('image', 'tag')