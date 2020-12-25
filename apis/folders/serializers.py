from rest_framework import serializers

from .models import Folders
from ..images.models import Images


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folders
        fields = ('id', 'title', 'owner_id', 'parent_id')


class CreateOrUpdateFolderSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=45)
    parent_id = serializers.IntegerField(min_value=0)


class FolderDetailSerializer(serializers.ModelSerializer):
    sub_folders = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Folders
        fields = ('id', 'title', 'owner_id', 'parent_id', 'sub_folders', 'images')

    def get_sub_folders(self, obj):
        sub_folders = Folders.objects.filter(parent_id=obj.id)
        data = []
        for folder in sub_folders:
            item = {'id': folder.id, 'title': folder.title}
            data.append(item)
        return data

    def get_images(self, obj):
        images = Images.objects.filter(folder_id=obj.id)
        data = []
        for image in images:
            item = {
                'id': image.id,
                'title': image.title,
                'path': image.path,
                'thumbnail_path': image.thumbnail_path
            }
            data.append(item)
        return data
