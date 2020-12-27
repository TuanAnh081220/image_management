from rest_framework import serializers
from .models import Tags, Images_Tags
from apis.images.models import Images
from ..images.serializers import DetailedImageSerializer, ImageSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'created_at', 'updated_at')


# class TagImageSerializer(serializers.ModelSerializer):
#     #img_title = serializers.CharField(source='image.title')
#     class Meta:
#         model = Images_Tags
#         fields = ('image',)

class ImageTagSerializer(serializers.ModelSerializer):
    # tag_name = serializers.CharField(source='tag.name')
    class Meta:
        model = Images_Tags
        fields = 'tag_name'


class TagDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Tags
        fields = ('id', 'name', 'owner_id', 'created_at', 'updated_at', 'images')

    def get_images(self, obj):
        images_tags = Images_Tags.objects.filter(tag=obj)
        image_list = []
        for pair in images_tags:
            image = Images.objects.get(id=pair.image_id)
            image_list.append(image)
        serializer = ImageSerializer(image_list, many=True)
        return serializer.data


class TagCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=45)


class SetImageTagSerializer(serializers.Serializer):
    select_all = serializers.BooleanField()
    image_id = serializers.ListField(
        child=serializers.IntegerField()
    )
    tag_id = serializers.ListField(
        child=serializers.IntegerField()
    )


class RemoveImageTagSerializer(serializers.Serializer):
    tag_id = serializers.IntegerField()


class TagRemoveSerializer(serializers.Serializer):
    tag_name = serializers.CharField()


class ImageFilteringByTagSerializer(serializers.Serializer):
    tag_list = serializers.ListField(
        child=serializers.IntegerField()
    )
