from rest_framework import serializers

from .models import Folders


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folders
        fields = ('id', 'title', 'owner_id', 'parent_id')


class CreateFolderSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=45)
    parent_id = serializers.IntegerField(min_value=0)
