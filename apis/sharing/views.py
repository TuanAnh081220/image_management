import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apis.folders.models import Folders
from apis.images.models import Images
from apis.sharing.serializers import SharingImageSerializer, SharedImageSerializer, SharingFolderSerializer, \
    SharedFolderSerializer
from apis.sharing.models import Shared_Images, Shared_Folders
from apis.users.models import Users
from utils.user import get_user_id_from_jwt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_image(request):
    owner_id = get_user_id_from_jwt(request)
    serializer = SharingImageSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    image_id_list = serializer.data['image_id']
    for image_id in image_id_list:
        try:
            Images.objects.get(id=image_id, owner_id = owner_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Image not found'
            }, status=status.HTTP_404_NOT_FOUND)

    user_id_list = serializer.data['user_id']
    for user_id in user_id_list:
        try:
            Users.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    for user_id in user_id_list:
        for image_id in image_id_list:
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            Shared_Images.objects.create(image_id=image_id, shared_user_id=user_id,
                                         created_at=created_at, updated_at=updated_at)
    return JsonResponse({
        'message': 'Image shared'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shared_image(request):
    user_id = get_user_id_from_jwt(request)
    shared_images = Shared_Images.objects.filter(shared_user_id=user_id)
    serializer = SharedImageSerializer(shared_images, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_folder(request):
    owner_id = get_user_id_from_jwt(request)
    serializer = SharingFolderSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    folder_id_list = serializer.data['folder_id']
    for folder_id in folder_id_list:
        try:
            Folders.objects.get(id=folder_id, owner_id = owner_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Folder not found'
            }, status=status.HTTP_404_NOT_FOUND)

    user_id_list = serializer.data['user_id']
    for user_id in user_id_list:
        try:
            Users.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    for user_id in user_id_list:
        for folder_id in folder_id_list:
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            Shared_Folders.objects.create(folder_id=folder_id, shared_user_id=user_id,
                                         created_at=created_at, updated_at=updated_at)
    return JsonResponse({
        'message': 'Folders shared'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shared_folder(request):
    user_id = get_user_id_from_jwt(request)
    shared_folders = Shared_Folders.objects.filter(shared_user_id=user_id)
    serializer = SharedFolderSerializer(shared_folders, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)