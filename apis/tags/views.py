from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from rest_framework import status, generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from utils.user import get_user_id_from_jwt

from .serializers import TagSerializer, TagCreateSerializer, TagDetailSerializer, SetImageTagSerializer, \
     ImageFilteringByTagSerializer,  RemoveImageTagSerializer
from .models import Tags, Images_Tags
from ..images.models import Images
from ..images.serializers import ImageSerializer
from ..images.views import get_image_by_id


class TagsList(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Tags.objects.filter(Q(owner=None) | Q(owner_id=user_id)).order_by('-updated_at')

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tag_detail(request, tag_id):
    tags = Tags.objects.filter(id=tag_id)
    serializer = TagDetailSerializer(tags, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tag_create(request):
    serializer = TagCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    tag_name = serializer.data['name']
    try:
        Tags.objects.get(name=tag_name)
    except ObjectDoesNotExist:
        owner_id = get_user_id_from_jwt(request)
        Tags.objects.create(name=tag_name, owner_id=owner_id)
        return JsonResponse({
            'message': 'Tag created'
        }, status=status.HTTP_200_OK)
    return JsonResponse({
        'message': 'Tag existed'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_image_by_tag(request):
    serializer = ImageFilteringByTagSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    owner_id = get_user_id_from_jwt(request)
    user_images = Images.objects.filter(owner_id=owner_id)
    image_list = []
    for image in user_images:
        image_list.append(image.id)
    tag_list = serializer.data['tag_list']
    for tag_id in tag_list:
        if Tags.objects.get(id=tag_id).owner_id != owner_id:
            return JsonResponse({
                'message': 'Inappropriate tag'
            }, status=status.HTTP_400_BAD_REQUEST)

    for tag_id in tag_list:
        for image_id in image_list:
            try:
                Images_Tags.objects.get(tag_id=tag_id, image_id=image_id)
            except ObjectDoesNotExist:
                image_list.remove(image_id)
    filtered_list = []
    for image_id in image_list:
        filtered_list. append(Images.objects.get(id=image_id))
    result = ImageSerializer(filtered_list, many=True)
    return JsonResponse(result.data, status=status.HTTP_200_OK, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_image_tag(request):
    user_id = get_user_id_from_jwt(request)
    serializer = SetImageTagSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid serializer'
        }, status=status.HTTP_400_BAD_REQUEST)
    select_all = serializer.data['select_all']
    if select_all:
        try:
            image_list = Images.objects.filter(owner_id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Image does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        image_id = serializer.data['image_id']
        image_list = []
        for id in image_id:
            try:
                image = Images.objects.get(id=id)
            except ObjectDoesNotExist:
                return JsonResponse({
                    'message': 'Image does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
            image_list.append(image)
    tag_id = serializer.data['tag_id']
    tag_list = []
    for id in tag_id:
        try:
            tag = Tags.objects.get(id=id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Tag does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        tag_list.append(tag)
    for image in image_list:
        for tag in tag_list:
            try:
                Images_Tags.objects.get(image=image, tag=tag)
            except ObjectDoesNotExist:
                Images_Tags.objects.create(image=image, tag=tag)
            else:
                pass
    return JsonResponse({
        'message': 'Tag added'
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_image_tag(request, image_id):
    serializer = RemoveImageTagSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    tag_id = serializer.data['tag_id']
    try:
        Images_Tags.objects.get(image_id=image_id, tag_id=tag_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': "Image doesn't have this tag"
        }, status=status.HTTP_404_NOT_FOUND)
    Images_Tags.objects.filter(image_id=image_id, tag_id=tag_id).delete()
    return JsonResponse({
        'message': 'Tag removed'
    }, status=status.HTTP_200_OK)

