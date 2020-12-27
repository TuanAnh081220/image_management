from rest_framework import serializers
from .models import Images



class UploadImagesSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(min_value=0)


class DetailedImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = ('id', 'title', 'thumbnail', 'owner_id', 'folder_id', 'star', 'size')


class TrashImageSerializer(serializers.Serializer):
    status = serializers.BooleanField()


# class MultipleImageIDsSerializer(serializers.Serializer):
#     ids = serializers.ListField(
#         child=serializers.IntegerField(min_value=0)
#     )

class MoveImageToFolderSerializer(serializers.Serializer):
    select_all = serializers.BooleanField()
    src_folder_id = serializers.IntegerField()
    dest_folder_id = serializers.IntegerField()
    image_id = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )



class ImageIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('id', 'title', 'image',)

# class ThumbnailPathImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Images
#         fields = ('thumbnail_path', )