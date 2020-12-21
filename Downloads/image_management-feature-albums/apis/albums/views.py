from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from datetime import datetime
from utils.user import get_user_id_from_jwt
from .models import Albums, AlbumsHaveImages

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

from .serializer import AlbumsSerializer, DetailedAlbumSerializer
# Create your views here.
from ..images.serializers import MultipleImageIDsSerializer

#
# class GetAlbums(APIView):
#     def get(self, request):
#         list_album = Albums.

class AlbumsList(generics.ListAPIView):
    serializer_class = AlbumsSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['star']
    search_fields = ['title']

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Albums.objects.filter(owner=user_id).order_by('-updated_at')


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_detailed_album(request, album_id):
    album = Albums.objects.get(id=album_id)
    if album is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    # user_id = get_user_id_from_jwt(request)
    #
    # if not is_owner(album.owner.id, user_id):
    #     return JsonResponse({
    #         "message": "permission denied"
    #     }, status=status.HTTP_403_FORBIDDEN)

    serializer = DetailedAlbumSerializer(instance=album)
    return JsonResponse({
        "album": serializer.data
    }, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def delete_album(request, album_id):
#     album = get_album_by_id(album_id)
#     if album is None:
#         return HttpResponse(status=status.HTTP_404_NOT_FOUND)

#     user_id = get_user_id_from_jwt(request)

#     if not is_owner(album.owner.id, user_id):
#         return JsonResponse({
#             "message": "permission denied"
#         }, status=status.HTTP_403_FORBIDDEN)

#     album = change_album_trash_status(album, True)
#     return JsonResponse({
#         "ialbum_id": album.id,
#         "is_trashed": album.is_trashed
#     }, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def delete_multiple_albums(request):
#     user_id = get_user_id_from_jwt(request)
#     serializer = MultipleImageIDsSerializer(data=request.data)
#     if not serializer.is_valid():
#         print("something")
#         return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
#     album_ids = serializer.data['ids']
#     for album_id in album_ids:
#         album = get_album_by_id(album_id)
#         if album is None:
#             return HttpResponse(status=status.HTTP_404_NOT_FOUND)
#         if not is_owner(album.owner.id, user_id):
#             return JsonResponse({
#                 "message": "permission denied for image id {}".format(album_id)
#             }, status=status.HTTP_403_FORBIDDEN)
#         change_album_trash_status(album, True)
#     return HttpResponse(status=status.HTTP_200_OK)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def update_album_title(request, album_id, title):
    try:
        album = Albums.objects.get(id=album_id)
        # user_id = get_user_id_from_jwt(request)
        #
        # if not is_owner(album.owner.id, user_id):
        #     return JsonResponse({
        #         "message": "permission denied"
        #     }, status=status.HTTP_403_FORBIDDEN)
        
        album.title = title   
        album.updated_at = datetime.now().time()   
        album.save()  
        return JsonResponse({
            "message": "success"
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def update_album_star(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
        # user_id = get_user_id_from_jwt(request)

        # if not is_owner(album.owner.id, user_id):
        #     return JsonResponse({
        #         "message": "permission denied"
        #     }, status=status.HTTP_403_FORBIDDEN)
        change_album_star_status(album, 1)
        return JsonResponse({
            "message": "success"
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def update_album_unstar(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
        # user_id = get_user_id_from_jwt(request)
        #
        # if not is_owner(album.owner.id, user_id):
        #     return JsonResponse({
        #         "message": "permission denied"
        #     }, status=status.HTTP_403_FORBIDDEN)
        change_album_star_status(album, 0)
        return JsonResponse({
            "message": "success"
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def change_album_star_status(instance, status):
    instance.star = status
    instance.updated_at = datetime.now().time()   
    instance.save()
    return instance


# def change_album_deleted_status(instance, status):
#     instance.is_trashed = status
#     instance.trashed_at = datetime.now()
#     instance.save()
#     return instance


def get_album_by_id(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
        return JsonResponse({"album_name": album.title}, safe=False)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def is_owner(owner_id, user_id):
    if owner_id != user_id:
        return False
    return True


def is_album_title_duplicate(owner_id, title):
    try:
        Albums.objects.get(owner_id=owner_id, title=title)
        return True
    except ObjectDoesNotExist:
        return False

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def delete_album(request, album_id):

    try:
        album = Albums.objects.get(id=album_id)
        # user_id = get_user_id_from_jwt(request)
        #
        # if not is_owner(album.owner.id, user_id):
        #     return JsonResponse({
        #         "message": "permission denied"
        #     }, status=status.HTTP_403_FORBIDDEN)

        AlbumsHaveImages.objects.filter(id=album_id).update(id=-1)
        album.delete()
        return JsonResponse ({
            "message": "success"
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def delete_all_removed_albums(request):
#     try:
#         albums = Albums.objects.filter(is_trashed=True)
#         user_id = get_user_id_from_jwt(request)

#         for album in albums:
#             if not is_owner(album.owner.id, user_id):
#                 return JsonResponse({
#                     "message": "permission denied"
#                 }, status=status.HTTP_403_FORBIDDEN)
#             AlbumsHaveImages.objects.filter(id=album.id).update(album_id=-1)
#             album.delete()
#         return JsonResponse ({
#             "message": "success"
#         }, status=status.HTTP_200_OK)

#     except ObjectDoesNotExist:
#         return HttpResponse(status=status.HTTP_404_NOT_FOUND)

# only filter removed albums
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_albums_filter_by_trashed_status(request):
#     try:
#         albums = Albums.object.filter(id=is_trashed=True)
#         user_id = get_user_id_from_jwt(request)
        
#         for album in albums:
#             if not is_owner(album.owner.id, user_id):
#                 return JsonResponse({
#                     "message": "permission denied"
#                 }, status=status.HTTP_403_FORBIDDEN)
#             return JsonResponse(albums, safe=False)
#     except ObjectDoesNotExist:
#         return HttpResponse(status=status.HTTP_404_NOT_FOUND)

# filter albums by star status
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_albums_filter_by_star_status(request, star):
    try:
        albums = Albums.objects.filter(star=star)
        # user_id = get_user_id_from_jwt(request)
        #
        # for album in albums:
        #     if not is_owner(album.owner.id, user_id):
        #         return JsonResponse({
        #             "message": "permission denied"
        #         }, status=status.HTTP_403_FORBIDDEN)s
        json_result = {}
        for album in albums:
            serializer = DetailedAlbumSerializer(instance=album)
            json_result[album.title] = serializer.data

        return JsonResponse({
            "albums": json.loads(json.dumps(json_result))
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)