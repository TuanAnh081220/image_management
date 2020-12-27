from rest_framework import serializers
from .models import Images



class UploadImagesSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(min_value=0)


class DetailedImageSerializer(serializers.ModelSerializer):
    thumbnail_size = serializers.SerializerMethodField()
    image_size = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Images
        fields = '__all__'

    def get_image_size(self, obj):
        data = {
            'width': obj.image.width,
            'height': obj.image.height
        }
        return data

    def get_thumbnail_size(self, obj):
        data = {
            'width': obj.thumbnail.width,
            'height': obj.thumbnail.height
        }
        return data

    def get_thumbnail_url(self, obj):
        return obj.thumbnail.url


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