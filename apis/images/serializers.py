from rest_framework import serializers
from .models import Images
from ..tags.models import Images_Tags, Tags


class UploadImagesSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField(min_value=0)


class DetailedImageSerializer(serializers.ModelSerializer):
    thumbnail_size = serializers.SerializerMethodField()
    image_size = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

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

    def get_tags(self, obj):
        images_tags = Images_Tags.objects.filter(image_id=obj.id)
        data = []
        for pair in images_tags:
            item = {
                'tag_id': pair.tag_id,
                'tag_name': Tags.objects.get(id=pair.tag_id).name
            }
            data.append(item)
        return data




class ImageSerializer(serializers.ModelSerializer):
    thumbnail_path = serializers.SerializerMethodField()

    class Meta:
        model = Images
        fields = ('id', 'title', 'image', 'owner_id', 'star', 'size', 'thumbnail_path')

    def get_thumbnail_path(self, obj):
        return obj.thumbnail.url


class TrashImageSerializer(serializers.Serializer):
    status = serializers.BooleanField()


class MultipleImageIDsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )

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