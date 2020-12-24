from rest_framework import serializers

from apis.folders.models import Folders
from apis.images.models import Images
from apis.sharing.models import Shared_Images, Shared_Folders


class SharingImageSerializer(serializers.Serializer):
    image_id = serializers.ListField(
        child=serializers.IntegerField()
    )
    user_id = serializers.ListField(
        child=serializers.IntegerField()
    )


class SharedImageSerializer(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()
    image_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Shared_Images
        fields = ('image_id', 'owner_id', 'image_thumbnail')

    def get_owner_id(self, obj):
        return Images.objects.get(id=obj.image.id).owner_id

    def get_image_thumbnail(self, obj):
        return Images.objects.get(id=obj.image.id).thumbnail_path


class SharingFolderSerializer(serializers.Serializer):
    folder_id = serializers.ListField(
        child=serializers.IntegerField()
    )
    user_id = serializers.ListField(
        child=serializers.IntegerField()
    )

class SharedFolderSerializer(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()
    folder_title = serializers.SerializerMethodField()

    class Meta:
        model = Shared_Folders
        fields = ('owner_id', 'folder_title')

    def get_owner_id(self, obj):
        return Folders.objects.get(id=obj.folder.id).owner_id

    def get_folder_title(self, obj):
        return Folders.objects.get(id=obj.folder.id).title