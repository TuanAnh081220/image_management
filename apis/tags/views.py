from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from utils.user import get_user_id_from_jwt

from .serializers import GetAllTagSerializer, TagCreateSerializer
from .models import Tags


# Create your views here.
@api_view(['GET'])
def tag_list(request):
    tags = Tags.objects.all()
    serializer = GetAllTagSerializer(tags, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def tag_detail(request, name):
    tags = Tags.objects.get(name=name)
    serializer = GetAllTagSerializer(tags, many=False)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
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
        #owner_id = get_user_id_from_jwt(request)
        owner_id = 1
        new_tag = Tags.objects.create(name=tag_name, owner_id=owner_id)
        return JsonResponse({
            'message': 'Tag created'
        }, status=status.HTTP_200_OK)
    return JsonResponse({
        'message': 'Tag existed'
    }, status=status.HTTP_400_BAD_REQUEST)