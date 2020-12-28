from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from utils.user import get_user_id_from_jwt
from .models import Albums, Albums_Images
from apis.images.models import Images
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

from .serializer import AlbumsSerializer, DetailedAlbumSerializer, UpdateOrCreateAlbumSerializer, \
    SelectImages, ListImageInAlbum, DeleteImageFromAlbum, AddMultipleImagesToMultipleAlbumsSerializer
from apis.images.serializers import ImageIdSerializer, ImageSerializer, DetailedImageSerializer


# class AlbumsList(generics.ListAPIView):
#
#     permission_classes = [IsAuthenticated]
#     serializer_class = AlbumsSerializer()
#     filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
#     filterset_fields = ['star']
#     search_fields = ['title', "created_at"]
#     ordering_fields = ['title', 'updated_at', 'created_at']
#
#     def get_queryset(self):
#         user_id = get_user_id_from_jwt(self.request)
#         return Albums.objects.filter(owner=user_id)

#
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_album(request):
    owner_id = get_user_id_from_jwt(request)
    data_albums = []
    try:
        # albums = Albums.objects.all().filter(owner_id=owner_id).order_by('-created_at')
        albums = Albums.objects.filter(owner_id=owner_id)
        for album in albums:
            data_images = {}
            try:
                album_id = AlbumsSerializer(instance=album).data['id']
                images = Images.objects.all().raw(
                    "SELECT id FROM images WHERE id IN (SELECT image_id FROM albums_have_images WHERE album_id = {}) "
                    "AND is_trashed=false".format(
                        album_id))

                serializer = AlbumsSerializer(instance=album)
                user_id = get_user_id_from_jwt(request)

                for image in images:
                    if not is_owner(image.owner.id, user_id):
                        return JsonResponse({
                            "message": "permission denied"
                        }, status=status.HTTP_403_FORBIDDEN)
                    break
                data_for_album = serializer.data
                data_for_album["total_images"] = len(images)
                data_images['info'] = data_for_album
                if len(images) > 0:
                    for image in images:
                        data_images['thumbnail'] = DetailedImageSerializer(instance=image).data['image']
                else:
                    data_images['thumbnail'] = ''
            except ObjectDoesNotExist:
                return JsonResponse({
                    "message": "image not found"
                }, status=status.HTTP_404_NOT_FOUND)
            # print(data_albums[0])
            data_albums.append(data_images)
    except ObjectDoesNotExist:
        return JsonResponse({
            "message": "album not found"
        }, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse({
        "albums": json.loads(json.dumps(data_albums))
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_album(request):
    serializer = UpdateOrCreateAlbumSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse({
            "message": "invalid album information"
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        owner_id = get_user_id_from_jwt(request)
    except Exception:
        return JsonResponse({
            "message": "no owner found"
        }, status=status.HTTP_403_FORBIDDEN)
    title = serializer.data['title']
    if is_album_title_duplicate(owner_id, title):
        title = title + "_duplicated"
    new_album = Albums.objects.create(
        title=title,
        owner_id=owner_id
    )
    return JsonResponse({
        "message": "successfully created",
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_album_title(request, album_id):
    album, err = find_album(request, album_id)
    if album is None:
        return err
    serializer = UpdateOrCreateAlbumSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            "message": "invalid album information"
        }, status=status.HTTP_400_BAD_REQUEST)

    album.title = serializer.data['title']
    album.update_at = datetime.now().time()
    album.save()

    return JsonResponse({
        "message": "successfully"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_album_star(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
        user_id = get_user_id_from_jwt(request)

        if not is_owner(album.owner.id, user_id):
            return JsonResponse({
                "message": "permission denied"
            }, status=status.HTTP_403_FORBIDDEN)
        change_album_star_status(album, 1)
        return JsonResponse({
            "message": "successfully"
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_album_unstar(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
        user_id = get_user_id_from_jwt(request)

        if not is_owner(album.owner.id, user_id):
            return JsonResponse({
                "message": "permission denied"
            }, status=status.HTTP_403_FORBIDDEN)
        change_album_star_status(album, 0)
        return JsonResponse({
            "message": "successfully"
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_album(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
        user_id = get_user_id_from_jwt(request)

        if not is_owner(album.owner.id, user_id):
            return JsonResponse({
                "message": "permission denied"
            }, status=status.HTTP_403_FORBIDDEN)

        Albums_Images.objects.filter(id=album_id).update(id=-1)
        album.delete()
        return JsonResponse({
            "message": "successfully"
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_albums_filter_by_star_status(request, star):
    try:
        albums = Albums.objects.filter(star=star)
        user_id = get_user_id_from_jwt(request)

        for album in albums:
            if not is_owner(album.owner.id, user_id):
                return JsonResponse({
                    "message": "permission denied"
                }, status=status.HTTP_403_FORBIDDEN)
        json_result = {}
        for album in albums:
            serializer = DetailedAlbumSerializer(instance=album)
            json_result[album.title] = serializer.data

        return JsonResponse({
            "albums": json.loads(json.dumps(json_result))
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_image_to_album(request, album_id):
    owner_id = get_user_id_from_jwt(request)
    serializer = SelectImages(data=request.data)
    album = get_album_by_id(album_id)
    if not is_owner(album.owner.id, owner_id):
        return JsonResponse({
            "message": "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    if not serializer.is_valid():
        return JsonResponse({
            "message": "Invalid serializer"
        }, status=status.HTTP_400_BAD_REQUEST)

    images = []
    select_all = serializer.data['select_all']
    if select_all:
        try:
            images = Images.objects.all().filter(owner_id=owner_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                "message": "Invalid image"
            })
    else:
        image_id = serializer.data['image_id']
        try:
            for id in image_id:
                images.append(Images.objects.get(id=id, owner_id=owner_id))
        except ObjectDoesNotExist:
            return JsonResponse({
                "message": "Image not found"
            })
    already_images = []
    for image in images:
        try:
            Albums_Images.objects.get(album_id=album_id, image_id=image.id)
            already_images.append(image.id)
        except ObjectDoesNotExist:
            Albums_Images.objects.create(album=album, image_id=image.id)
        # return JsonResponse({
        #     "message": "Album already had this image"
        # }, status=status.HTTP_400_BAD_REQUEST)
    if len(already_images) == 0:
        return JsonResponse({
            "message": "successfully"
        }, status=status.HTTP_200_OK)
    else:
        return JsonResponse({
            "message": "Album already had image id {}".format(already_images)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detailed_album(request, album_id):
    album = Albums.objects.get(id=album_id)
    if album is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    user_id = get_user_id_from_jwt(request)

    if not is_owner(album.owner.id, user_id):
        return JsonResponse({
            "message": "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = DetailedAlbumSerializer(instance=album)
    image = Images.objects.raw(
        "SELECT id FROM images WHERE id IN (SELECT image_id FROM albums_have_images WHERE album_id = {}) AND "
        "is_trashed = false".format(
            album_id))
    image_id_serializer = DetailedImageSerializer(image, many=True)

    data = serializer.data
    data['total_images'] = len(image)
    data['images'] = image_id_serializer.data

    return JsonResponse({
        "album": data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_image_in_album(request, album_id):
    owner_id = get_user_id_from_jwt(request)
    serializer = SelectImages(data=request.data)
    album = get_album_by_id(album_id)

    if not is_owner(album.owner.id, owner_id):
        return JsonResponse({
            "message": "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    if not serializer.is_valid():
        return JsonResponse({
            "message": "Invalid image information"
        }, status=status.HTTP_400_BAD_REQUEST)
    select_all = serializer.data['select_all']
    invalid_image = []
    if select_all:
        try:
            images = Albums_Images.objects.all().filter(album_id=album_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                "message": "Invalid image"
            })
        for image in images:
            Albums_Images.objects.get(album_id=album_id, image_id=image.images_id).delete()
        return JsonResponse({
            "message": "successfully"
        })

    else:
        image_id = serializer.data['images_id']
        for id in image_id:
            try:
                Albums_Images.objects.get(album_id=album_id, image_id=id).delete()
            except ObjectDoesNotExist:
                invalid_image.append(id)
        if len(invalid_image) > 0:
            return JsonResponse({
                "message": "Album doesn't have image id {}".format(invalid_image)
            })
        else:
            return JsonResponse({
                "message": "successfully"
            })



    # print(images)
    # for image in images:
    #     try:
    #         AlbumsHaveImages.objects.get(album_id=album_id, image_id=image.image_id).delete()
    #     except ObjectDoesNotExist:
    #         invalid_image.append(image.album_id)
    # if len(invalid_image) > 0:
    #     return JsonResponse({
    #         "message": "Album doesn't have image id {}".format(invalid_image)
    #     })
    # else:
    #     return JsonResponse({
    #         "message": "successfully"
    #     }, status=status.HTTP_200_OK)

    # try:
    #     Images.objects.get(id=image_id, owner_id=owner_id)
    # except ObjectDoesNotExist:
    #     return JsonResponse({
    #         "message": "Image does not exist"
    #     }, status=status.HTTP_404_NOT_FOUND)
    # try:
    #     AlbumsHaveImages.objects.get(album_id=album_id, image_id=image_id).delete()
    #     return JsonResponse({
    #         "message": "sucessfully"
    #     }, status=status.HTTP_200_OK)
    # except ObjectDoesNotExist:
    #     return JsonResponse({
    #         "message": "Album doesn't have image"
    #     }, status=status.HTTP_200_OK)


def change_album_star_status(instance, status):
    instance.star = status
    instance.updated_at = datetime.now().time()
    instance.save()
    return instance


def get_album_by_id(album_id):
    try:
        album = Albums.objects.get(id=album_id)
        return album
    except ObjectDoesNotExist:
        return None


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


def find_album(request, album_id):
    try:
        album = Albums.objects.get(id=album_id)
    except ObjectDoesNotExist:
        return None, JsonResponse({
            "message": "no album with id {} found".format(album_id)
        }, status=status.HTTP_404_NOT_FOUND)

    return album, None

# def change_album_deleted_status(instance, status):
#     instance.is_trashed = status
#     instance.trashed_at = datetime.now()
#     instance.save()
#     return instance

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
