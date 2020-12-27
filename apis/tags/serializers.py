from rest_framework import serializers
from .models import Tags, Images_Tags
from apis.images.models import Images


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
    # images = TagImageSerializer(source='tag_image', many=True)
    class Meta:
        model = Tags
        fields = '__all__'

    def get_images(self, obj):
        return obj.id


class GetImageTagSerializer(serializers.ModelSerializer):
    tags = ImageTagSerializer(source='image_tag', many=True)

    class Meta:
        model = Images
        fields = ('id', 'title', 'tags')


class TagCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=45)


class SetImageTagSerializer(serializers.Serializer):
    # image_id = serializers.IntegerField()
    tag_id = serializers.IntegerField()


class RemoveImageTagSerializer(serializers.Serializer):
    tag_id = serializers.IntegerField()


class TagRemoveSerializer(serializers.Serializer):
    tag_name = serializers.CharField()


class ImageFilteringByTagSerializer(serializers.Serializer):
    tag_list = serializers.ListField(
        child=serializers.IntegerField()
    )
