from rest_framework import serializers
from .models import Albums
from apis.images.models import Images

class AlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('id', 'title', 'star', 'owner_id')

class DetailedAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = '__all__'

class UpdateOrCreateAlbumSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=45)

class AddImageToAlbumSerializer(serializers.Serializer):
    image_id = serializers.IntegerField()

class ListImageInAlbum(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('id', 'title')