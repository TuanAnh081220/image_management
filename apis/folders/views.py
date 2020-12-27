from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.user import get_user_id_from_jwt
from utils.serializers import MultiplIDsSerializer
from .serializers import FolderSerializer, CreateOrUpdateFolderSerializer, FolderDetailSerializer
from .models import Folders
from ..users.views import get_user_from_id
from ..images.models import Images
from ..images.serializers import ImageSerializer

from datetime import datetime


class FoldersList(generics.ListAPIView):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Folders.objects.filter(owner_id=user_id, parent_id=0, is_trashed=False).order_by('-updated_at')


class FoldersListTrash(generics.ListAPIView):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Folders.objects.filter(owner_id=user_id, parent_id=0, is_trashed=True).order_by('-updated_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_folder_list(request):
    user_id = get_user_id_from_jwt(request)
    folders = Folders.objects.filter(owner_id=user_id, parent_id=0).order_by('-updated_at')
    serializer = FolderDetailSerializer(folders, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_folder(request):
    serializer = CreateOrUpdateFolderSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'invalid folder information'
        }, status=status.HTTP_400_BAD_REQUEST)
    owner_id = get_user_id_from_jwt(request)
    try:
        owner = get_user_from_id(owner_id)
    except Exception:
        return JsonResponse({
            'message': 'no owner found'
        }, status=status.HTTP_403_FORBIDDEN)
    title = serializer.data['title']
    parent_id = serializer.data['parent_id']
    if is_folder_title_duplicate(owner_id, title):
        title = title + "_duplicated"
    new_folder = Folders.objects.create(
        title=title,
        parent_id=parent_id,
        owner=owner
    )
    return JsonResponse({
        'message': 'successfully created',
        'folder_id': new_folder.id
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detailed_folder(request, folder_id):
    folder, err = find_folder_and_check_permission(request, folder_id)
    if folder is None:
        return err

    serializer = FolderDetailSerializer(folder, many=False)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trash_folder(request, folder_id):
    folder, err = find_folder_and_check_permission(request, folder_id)
    if folder is None:
        return err

    change_folder_is_trashed_status(folder, True)

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trash_multiple_folder(request):
    folder_ids, err = check_multiple_ids_request(request)
    if err is not None:
        return err

    for folder_id in folder_ids:
        folder, err = find_folder_and_check_permission(request, folder_id)
        if folder is None:
            return err
        change_folder_is_trashed_status(folder, True)

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_multiple_folder(request):
    folder_ids, err = check_multiple_ids_request(request)
    if err is not None:
        return err

    for folder_id in folder_ids:
        folder, err = find_folder_and_check_permission(request, folder_id)
        if folder is None:
            return err
        change_folder_is_trashed_status(folder, False)

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_multiple_folder(request):
    folder_ids, err = check_multiple_ids_request(request)
    if err is not None:
        return err

    for folder_id in folder_ids:
        folder, err = find_folder_and_check_permission(request, folder_id)
        if folder is None:
            return err
        delete_folder(folder)

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_folder(request, folder_id):
    folder, err = find_folder_and_check_permission(request, folder_id)
    if folder is None:
        return err

    change_folder_is_trashed_status(folder, False)

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_folder(request, folder_id):
    folder, err = find_folder_and_check_permission(request, folder_id)
    if folder is None:
        return err
    delete_folder(folder)
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_folder(request, folder_id):
    folder, err = find_folder_and_check_permission(request, folder_id)
    if folder is None:
        return err

    serializer = CreateOrUpdateFolderSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'invalid folder information'
        }, status=status.HTTP_400_BAD_REQUEST)

    folder.title = serializer.data['title']
    folder.parent_id = serializer.data['parent_id']
    folder.save()

    return JsonResponse({
        'message': 'successfully updated'
    }, status=status.HTTP_200_OK)


def check_multiple_ids_request(request):
    serializer = MultiplIDsSerializer(data=request.data)
    if not serializer.is_valid():
        return None, JsonResponse({
            'message': 'invalid request'
        }, status=status.HTTP_400_BAD_REQUEST)

    folder_ids = serializer.data['ids']

    if len(folder_ids) == 0:
        return None, JsonResponse({
            'message': 'empty request'
        }, status=status.HTTP_400_BAD_REQUEST)

    return folder_ids, None


def find_folder_and_check_permission(request, folder_id):
    try:
        folder = Folders.objects.get(id=folder_id)
    except ObjectDoesNotExist:
        return None, JsonResponse({
            'message': 'no folder with id {} found'.format(folder_id),
        }, status=status.HTTP_404_NOT_FOUND)

    user_id = get_user_id_from_jwt(request)
    if not is_owner(folder, user_id):
        return None, JsonResponse({
            'message': 'permission denied',
        }, status=status.HTTP_403_FORBIDDEN)

    return folder, None


def delete_folder(folder):
    sub_folders = Folders.objects.filter(parent_id=folder.id)
    for sub_folder in sub_folders:
        sub_folder.delete()
    images = Images.objects.filter(folder_id=folder.id)
    for image in images:
        image.detele()
    folder.delete()


def change_folder_is_trashed_status(folder, status):
    change_instance_is_trashed_status(folder, status)
    sub_folders = Folders.objects.filter(parent_id=folder.id)
    for sub_folder in sub_folders:
        change_folder_is_trashed_status(sub_folder, status)
    images = Images.objects.filter(folder_id=folder.id)
    for image in images:
        change_instance_is_trashed_status(image, status)


def change_instance_is_trashed_status(instance, status):
    instance.is_trashed = status
    instance.trashed_at = datetime.now()
    instance.save()


def is_owner(folder, user_id):
    if not folder.owner_id == user_id:
        return False
    return True


def is_folder_title_duplicate(owner_id, title):
    try:
        Folders.objects.get(owner_id=owner_id, title=title)
        return True
    except ObjectDoesNotExist:
        return False
