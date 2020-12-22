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

from .serializers import TagSerializer, TagCreateSerializer, TagDetailSerializer, SetImageTagSerializer, TagImageSerializer
from .models import Tags, Images_Tags


class TagsList(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Tags.objects.filter(Q(owner_id=0) | Q(owner_id=user_id)).order_by('-updated_at')

# Create your views here.
@api_view(['GET'])
def tag_list(request):
    tags = Tags.objects.all()
    serializer = TagSerializer(tags, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

@api_view(['GET'])
def tag_detail(request, tag_id):
    tags = Tags.objects.filter(tag_id=tag_id)
    serializer = TagDetailSerializer(tags, many=True)
    images = Images_Tags.objects.filter(tag_id=tag_id)
    serializer.data['images'] = images
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

