from rest_framework import serializers

from apis.images.models import Images
from apis.sharing.models import Shared_Images


class SharingImageSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


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
