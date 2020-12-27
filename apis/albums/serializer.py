from rest_framework import serializers
from .models import Albums, Albums_Images
from apis.images.models import Images


class AlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('id', 'title', 'star', 'owner_id', 'created_at')

    def get_images(self, obj):
        images = Albums_Images.objects.filter(album_id=obj.id)
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

class DetailedAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = '__all__'


class UpdateOrCreateAlbumSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=45)


class SelectImages(serializers.Serializer):
    select_all = serializers.BooleanField()
    image_id = serializers.ListField(
            child=serializers.IntegerField(min_value=0)
    )

class DeleteImageFromAlbum(serializers.Serializer):
    image_id = serializers.IntegerField(min_value=0)

class ListImageInAlbum(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('id', 'title')
