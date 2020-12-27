import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apis.folders.models import Folders
from apis.folders.serializers import FolderDetailSerializer
from apis.images.models import Images
from apis.images.serializers import DetailedImageSerializer
from apis.sharing.serializers import SharingImageSerializer, SharedImageSerializer, SharingFolderSerializer, \
    SharedFolderSerializer
from apis.sharing.models import Shared_Images, Shared_Folders
from apis.users.models import Users
from apis.users.views import get_user_from_id
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
    user_id_list = serializer.data['user_id']
    select_all = serializer.data['select_all']
    if select_all:
        folder_id = serializer.data['folder_id']
        try:
            image_list = Images.objects.filter(owner_id=owner_id, folder_id=folder_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Images not found'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        image_id_list = serializer.data['image_id']
        image_list = []
        for image_id in image_id_list:
            try:
                image = Images.objects.get(id=image_id, owner_id = owner_id)
            except ObjectDoesNotExist:
                return JsonResponse({
                    'message': 'Image not found'
                }, status=status.HTTP_404_NOT_FOUND)
            image_list.append(image)
    for user_id in user_id_list:
        try:
            Users.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    for user_id in user_id_list:
        for image in image_list:
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            Shared_Images.objects.create(image=image, shared_user_id=user_id,
                                         created_at=created_at, updated_at=updated_at)
    return JsonResponse({
        'message': 'Image shared'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_shared_image(request):
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
    folder_id = serializer.data['folder_id']
    try:
        Folders.objects.get(id=folder_id, owner_id=owner_id)
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
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()
        Shared_Folders.objects.create(folder_id=folder_id, shared_user_id=user_id,
                                     created_at=created_at, updated_at=updated_at)
    return JsonResponse({
        'message': 'Folders shared'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_shared_folders(request):
    user_id = get_user_id_from_jwt(request)
    shared_folders = Shared_Folders.objects.filter(shared_user_id=user_id)
    serializer = SharedFolderSerializer(shared_folders, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shared_folder_detail(request):
    user_id = get_user_id_from_jwt(request)
    shared_id = folder_id = request.data['folder_id']
    while shared_id != 0:
        try:
            Shared_Folders.objects.get(folder_id=shared_id, shared_user_id=user_id)
        except ObjectDoesNotExist:
            shared_id = Folders.objects.get(id=shared_id).parent_id
        else:
            folder = Folders.objects.get(id=folder_id)
            serializer = FolderDetailSerializer(folder, many=False)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    return JsonResponse({
        'message': 'Shared folder not found'
    }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shared_image_detail(request):
    user_id = get_user_id_from_jwt(request)
    image_id = request.data['image_id']
    try:
        image = Images.objects.get(id=image_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'Image not found'
        }, status=status.HTTP_404_NOT_FOUND)
    try:
        Shared_Images.objects.get(image_id=image_id, shared_user_id=user_id)
    except ObjectDoesNotExist:
        folder_id = image.folder_id
        while folder_id != 0:
            try:
                Shared_Folders.objects.get(folder_id=folder_id, shared_user_id=user_id)
            except ObjectDoesNotExist:
                folder_id = Folders.objects.get(id=folder_id).parent_id
            else:
                serializer = DetailedImageSerializer(image, many=False)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse({
            'message': 'Shared image not found'
        }, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedImageSerializer(image, many=False)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_image_to_collection(request):
    user_id = get_user_id_from_jwt(request)
    # serializer = AddImgToCollectionSerializer(data=request.data)
    # if not serializer.is_valid():
    #     return JsonResponse({
    #         'message': 'Invalid serializer'
    #     }, status=status.HTTP_400_BAD_REQUEST)

    folder_id = request.data['folder_id']
    if folder_id != 0:
        try:
            Folders.objects.get(id=folder_id, owner_id = user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Folder not found'
            }, status=status.HTTP_404_NOT_FOUND)

    select_all = request.data['select_all']
    if select_all:
        try:
            shared_list = Shared_Images.objects.filter(shared_user_id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Shared image not found'
            }, status=status.HTTP_404_NOT_FOUND)
        for connection in shared_list:
            img = Images.objects.get(id=connection.image_id)
            new_image = img
            new_image.pk = None
            new_image.owner = get_user_from_id(user_id)
            new_image.folder_id = folder_id
            new_image.image.save(img.title, img.image, True)
            new_image.star = new_image.is_trashed = False
            new_image.trashed_at = None
            new_image.created_at = new_image.updated_at = datetime.datetime.now()
            new_image.is_public = False
            new_image.save()
    else:
        image_id = request.data['image_id']
        for iterator in image_id:
            img = Images.objects.get(id=iterator)
            new_image = img
            new_image.pk = None
            new_image.owner = get_user_from_id(user_id)
            new_image.folder_id = folder_id
            new_image.image.save(img.title, img.image, True)
            new_image.star = new_image.is_trashed = False
            new_image.trashed_at = None
            new_image.created_at = new_image.updated_at = datetime.datetime.now()
            new_image.is_public = False
            new_image.save()
    return JsonResponse({
        'message': 'Added to user {} collection'.format(user_id)
    }, status=status.HTTP_200_OK)
