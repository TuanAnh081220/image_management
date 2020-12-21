from rest_framework import serializers
from .models import Albums

class AlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('id', 'title', 'star', 'owner_id')

class DetailedAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = '__all__'

