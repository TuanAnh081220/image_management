from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from utils.user import get_user_id_from_jwt
from .serializers import FolderSerializer, CreateFolderSerializer
from .models import Folders
from ..users.views import get_user_from_id
from ..images.models import Images
from ..images.serializers import ImageSerializer


class FoldersList(generics.ListAPIView):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Folders.objects.filter(owner_id=user_id, parent_id=0).order_by('-updated_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_folder(request):
    serializer = CreateFolderSerializer(data=request.data)
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
    try:
        folder = Folders.objects.get(id=folder_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'no folder found',
        }, status=status.HTTP_404_NOT_FOUND)

    user_id = get_user_id_from_jwt(request)
    if not is_owner(folder, user_id):
        return JsonResponse({
            'message': 'permission denied',
        }, status=status.HTTP_403_FORBIDDEN)

    folder_serializer = FolderSerializer(instance=folder)

    sub_folders = Folders.objects.filter(parent_id=folder.id)
    sub_folders_serializer = FolderSerializer(instance=sub_folders, many=True)

    images = Images.objects.filter(folder_id=folder.id)
    images_serializer = ImageSerializer(instance=images, many=True)

    return JsonResponse({
        'folder': folder_serializer.data,
        'sub_folders': sub_folders_serializer.data,
        'images': images_serializer.data
    }, status=status.HTTP_200_OK)




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
