from rest_framework import serializers
from .models import Images
from apis.tags.serializers import ImageTagSerializer


class UploadImagesSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(min_value=0)


class DetailedImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = ('id', 'title', 'path', 'owner_id', 'folder_id', 'star', 'size', 'is_trashed')


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = ('id', 'title', 'thumbnail_path', 'owner_id', 'folder_id', 'star', 'size')


class TrashImageSerializer(serializers.Serializer):
    status = serializers.BooleanField()


# class MultipleImageIDsSerializer(serializers.Serializer):
#     ids = serializers.ListField(
#         child=serializers.IntegerField(min_value=0)
#     )

class RemoveImageTagSerializer(serializers.Serializer):
    tag_id = serializers.IntegerField()

class ImageIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('id', 'title')