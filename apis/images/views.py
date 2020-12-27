import io
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from utils.user import get_user_id_from_jwt
from utils.serializers import MultiplIDsSerializer
from .serializers import UploadImagesSerializer, DetailedImageSerializer, \
    MoveImageToFolderSerializer, MultipleImageIDsSerializer
from ..albums.serializer import AddMultipleImagesToMultipleAlbumsSerializer
from .models import Images
from apis.users.views import get_user_from_id
from apis.tags.serializers import TagSerializer
from apis.folders.models import Folders
from apis.users.models import Users
import urllib.request

from datetime import datetime

import magic

from ..sharing.models import Shared_Images
from ..tags.models import Tags, Images_Tags
from ..albums.models import Albums_Images, Albums
from wsgiref.util import FileWrapper
import mimetypes


class ImagesList(generics.ListAPIView):
    serializer_class = DetailedImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['star']
    search_fields = ['title']

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Images.objects.filter(is_trashed=False, owner_id=user_id).order_by('-updated_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    if not request.FILES['images']:
        return JsonResponse({
            'message': 'no images uploaded'
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = UploadImagesSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'no given folder id'
        }, status=status.HTTP_400_BAD_REQUEST)
    folder_id = serializer.data['folder_id']
    owner_id = get_user_id_from_jwt(request)
    try:
        owner = get_user_from_id(owner_id)
    except Exception:
        return JsonResponse({
            'message': 'no owner found'
        }, status=status.HTTP_403_FORBIDDEN)

    for img in request.FILES.getlist('images'):
        title = img.name
        new_img = Images.objects.create(
            owner=owner,
            folder_id=folder_id,
            image=img,
            size=img.size,
            title=title
        )
        print(new_img.thumbnail.url)
    return JsonResponse({
        'message': 'successfully uploaded'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detailed_image(request, image_id):
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceAccountToken.json'
    # image = get_image_by_id(image_id)
    # if image is None:
    #     return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    #
    # user_id = get_user_id_from_jwt(request)
    #
    # if not is_owner(image.owner.id, user_id):
    #     return JsonResponse({
    #         'message': "permission denied"
    #     }, status=status.HTTP_403_FORBIDDEN)
    #
    # serializer = DetailedImageSerializer(instance=image)
    #
    # tag = Tags.objects.raw("select id from tags where id in (select tag_id from images_tags where image_id = 1)")
    #
    # tag_serializer = TagSerializer(tag, many=True)
    #
    # data = serializer.data
    # data['tags'] = tag_serializer.data
    #
    # # image_cloud = vision.Image(content=image)
    #
    #
    # # client = vision.ImageAnnotatorClient()
    # # response = client.label_detection(image=image_cloud)
    # # data['tag'] = response
    # return JsonResponse({
    #     'image': data
    # }, status=status.HTTP_200_OK)
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    user_id = get_user_id_from_jwt(request)

    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = DetailedImageSerializer(instance=image)
    return JsonResponse({
        'image': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trash_image(request, image_id):
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    user_id = get_user_id_from_jwt(request)

    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    image = change_image_trash_status(image, True)
    return JsonResponse({
        'image_id': image.id,
        'is_trashed': image.is_trashed
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trash_multiple_image(request):
    user_id = get_user_id_from_jwt(request)
    serializer = MultiplIDsSerializer(data=request.data)
    if not serializer.is_valid():
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    image_ids = serializer.data['ids']
    for image_id in image_ids:
        image = get_image_by_id(image_id)
        if image is None:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if not is_owner(image.owner.id, user_id):
            return JsonResponse({
                'message': "permission denied for image id {}".format(image_id)
            }, status=status.HTTP_403_FORBIDDEN)
        change_image_trash_status(image, True)
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_image(request, image_id):
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    user_id = get_user_id_from_jwt(request)
    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    image = change_image_trash_status(image, False)
    return JsonResponse({
        'image_id': image.id,
        'is_trashed': image.is_trashed
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_multiple_image(request):
    user_id = get_user_id_from_jwt(request)
    serializer = MultipleImageIDsSerializer(data=request.data)
    if not serializer.is_valid():
        print("something")
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    image_ids = serializer.data['ids']
    for image_id in image_ids:
        image = get_image_by_id(image_id)
        if image is None:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if not is_owner(image.owner.id, user_id):
            return JsonResponse({
                'message': "permission denied for image id {}".format(image_id)
            }, status=status.HTTP_403_FORBIDDEN)
        change_image_trash_status(image, False)
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_id):
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    user_id = get_user_id_from_jwt(request)
    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)
    # image.delete()
    try:
        Albums_Images.objects.get(image_id=image.id).delete()
        # message = "Successfully"
    except ObjectDoesNotExist:
        print("This image {} does not exist in album!".format(image.id))
    try:
        Images_Tags.objects.get(image_id=image.id).delete()
        # message = "Successfully"
    except ObjectDoesNotExist:
        print("This image {} does not have tag!".format(image.id))
    try:
        Shared_Images.objects.get(image_id=image.id).delete()
        # message = "Successfully"
    except ObjectDoesNotExist:
        print("This image {} is not shared!".format(image.id))
    try:
        img = image.image
        image.delete()
        img.delete()
        # message = "Successfully"
    except ObjectDoesNotExist:
        print("This image {} does not exist!".format(image.id))
    except ProtectedError:
        print("This image {} can't be deleted!!".format(image.id))
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_multiple_image(request):
    user_id = get_user_id_from_jwt(request)
    serializer = MultipleImageIDsSerializer(data=request.data)
    if not serializer.is_valid():
        print("something")
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    image_ids = serializer.data['ids']

    for image_id in image_ids:
        image = get_image_by_id(image_id)
        if image is None:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if not is_owner(image.owner.id, user_id):
            return JsonResponse({
                'message': "permission denied for image id {}".format(image_id)
            }, status=status.HTTP_403_FORBIDDEN)
        try:
            Albums_Images.objects.filter(image_id=image_id).delete()
            # message = "Successfully"
        except ObjectDoesNotExist:
            print("This image {} does not exist in album!".format(image.id))
        try:
            Images_Tags.objects.filter(image_id=image_id).delete()
            # message = "Successfully"
        except ObjectDoesNotExist:
            print("This image {} does not have tag!".format(image.id))
        try:
            Shared_Images.objects.filter(image_id=image_id).delete()
            # message = "Successfully"
        except ObjectDoesNotExist:
            print("This image {} is not shared!".format(image.id))
        try:
            image.delete()
            # message = "Successfully"
        except ObjectDoesNotExist:
            print("This image {} does not exist!".format(image.id))
        except ProtectedError:
            print("This image {} can't be deleted!!".format(image.id))
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_image(request):
    user_id = get_user_id_from_jwt(request)
    select_all = request.data['select_all']
    if select_all:
        folder_id = request.data['folder_id']
        if folder_id != 0:
            try:
                Folders.objects.get(id=folder_id)
            except ObjectDoesNotExist:
                return JsonResponse({
                    'message': 'Folder does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
        try:
            image_list = Images.objects.filter(folder_id=folder_id, owner_id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Images not found'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        image_id_list = request.data['image_id']
        image_list = []
        for id in image_id_list:
            try:
                image = Images.objects.get(id=id)
            except ObjectDoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

            if not is_owner(image.owner.id, user_id):
                return JsonResponse({
                    'message': "permission denied"
                }, status=status.HTTP_403_FORBIDDEN)
            image_list.append(image)

    for image in image_list:
        image.star = True
        image.save()
    return JsonResponse({
        'message': 'Add images to favourite'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def un_star_image(request):
    user_id = get_user_id_from_jwt(request)
    select_all = request.data['select_all']
    if select_all:
        folder_id = request.data['folder_id']
        if folder_id != 0:
            try:
                Folders.objects.get(id=folder_id)
            except ObjectDoesNotExist:
                return JsonResponse({
                    'message': 'Folder does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
        try:
            image_list = Images.objects.filter(folder_id=folder_id, owner_id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Images not found'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        image_id_list = request.data['image_id']
        image_list = []
        for id in image_id_list:
            try:
                image = Images.objects.get(id=id)
            except ObjectDoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)

            if not is_owner(image.owner.id, user_id):
                return JsonResponse({
                    'message': "permission denied"
                }, status=status.HTTP_403_FORBIDDEN)
            image_list.append(image)

    for image in image_list:
        image.star = False
        image.save()
    return JsonResponse({
        'message': 'Removed images from favourite'
    }, status=status.HTTP_200_OK)


def change_image_star_status(instance, status):
    instance.star = status
    instance.save()
    return instance


def change_image_trash_status(instance, status):
    instance.is_trashed = status
    instance.trashed_at = datetime.now()
    instance.save()
    return instance


def get_image_by_id(image_id):
    try:
        image = Images.objects.get(id=image_id)
        return image
    except ObjectDoesNotExist:
        return None


def is_owner(owner_id, user_id):
    if owner_id != user_id:
        return False
    return True


def is_image_title_duplicate(owner_id, title):
    try:
        Images.objects.get(owner_id=owner_id, title=title)
        return True
    except ObjectDoesNotExist:
        return False


@api_view(['POST'])
def test_upload_image_view(request):
    # # print(request.data['title'])
    # # print(type(request.FILES['content']))
    # # print(request.FILES['content'])
    # # myfile = request.FILES['content']
    # # fs = FileSystemStorage()
    # # filename = fs.save(myfile.name, myfile)
    # # uploaded_file_url = fs.url(filename)
    # myfiles = request.FILES.getlist('content')
    #
    #
    #
    # print(dir(request.FILES))
    #
    # file = request.data.get("content")  # type(file) = 'django.core.files.uploadedfile.InMemoryUploadedFile'
    # print(file.content_type)
    #
    # images_serializer = ImageSerializer(data=request.FILES)
    #
    # if images_serializer.is_valid():
    #     print(images_serializer.data)
    #     print("valid image")
    # else:
    #     # print(images_serializer.data)
    #     # print(images_serializer.e)
    #     print("invalid image")

    # print(request.headers)

    my_file = request.FILES['content']
    #
    b = io.BytesIO(my_file.file.getvalue())
    print(type(b.read()))
    print(magic.from_buffer(b.read(), mime=True))
    # print(mime.from_buffer(b.read()), mime=True)

    # f = io.BytesIO(my_file.file)

    # print(my_file.file.getvalue())
    # for file in myfiles:
    #     print(dir(file))
    #     print(file.content_type)
    #     print(file.size)
    #     # print(file.name)
    #     # print(file.type)
    # print(type(myfiles))
    # # print(myfiles.name)
    # # print(request.FILES['content'])
    #
    # serializer = UploadImageSerializer(data=request.data)
    # if serializer.is_valid():
    #     print("something")
    # else:
    #     print("haha")

    # print(uploaded_file_url)
    return JsonResponse({
        'user': "hihi"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_image_to_folder(request):
    user_id = get_user_id_from_jwt(request)

    serializer = MoveImageToFolderSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)

    dest_folder_id = serializer.data['dest_folder_id']
    if dest_folder_id != 0:
        try:
            Folders.objects.get(id=dest_folder_id, owner_id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'Destination folder not found'
            }, status=status.HTTP_404_NOT_FOUND)

    select_all = serializer.data['select_all']
    if select_all:
        src_folder_id = serializer.data['src_folder_id']
        if src_folder_id != 0:
            try:
                Folders.objects.get(id=src_folder_id, owner_id=user_id)
            except ObjectDoesNotExist:
                return JsonResponse({
                    'message': 'Source folder not found'
                }, status=status.HTTP_404_NOT_FOUND)
        try:
            images = Images.objects.filter(folder_id=src_folder_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                'message': 'No images selected'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        images = []
        image_id = serializer.data['image_id']
        for id in image_id:
            try:
                images.append(Images.objects.get(id=id))
            except ObjectDoesNotExist:
                return JsonResponse({
                    'message': 'Image not found'
                }, status=status.HTTP_404_NOT_FOUND)
    for image in images:
        image.folder_id = dest_folder_id
        image.updated_at = datetime.now()
        image.save()
    return JsonResponse({
        'message': 'Image moved'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_multiple_images_to_multiple_albums(request):
    owner_id = get_user_id_from_jwt(request)
    serializer = AddMultipleImagesToMultipleAlbumsSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            "message": "Invalid Serializer"
        }, status=status.HTTP_400_BAD_REQUEST)

    albums_id = serializer.data['albums_id']
    for album_id in albums_id:
        try:
            Albums.objects.get(id=album_id, owner_id=owner_id)
        except ObjectDoesNotExist:
            return JsonResponse({
                "message": "Album not found"
            }, status=status.HTTP_404_NOT_FOUND)

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
        image_id = serializer.data['images_id']
        try:
            for id in image_id:
                images.append(Images.objects.get(id=id, owner_id=owner_id))
        except ObjectDoesNotExist:
            return JsonResponse({
                "message": "Image not found"
            })
    for album_id in albums_id:
        for image in images:
            try:
                Albums_Images.objects.get(album_id=album_id, image_id=image.id)
            except ObjectDoesNotExist:
                Albums_Images.objects.create(album_id=album_id, image_id=image.id)

    return JsonResponse({
        "message": "successfully"
    })


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def download_image(request, image_id):
    # image_id = request.data['image_id']
    img = Images.objects.get(id=image_id)
    # # try:
    # #     urllib.request.urlretrieve("http://127.0.0.1:8080" + str(img.image.url), str(img.image.url))
    # #     return JsonResponse({
    # #         "message" : "success"
    # #     })
    # # except FileNotFoundError:
    # #     return JsonResponse({
    # #         "message": "File not found"
    # #     })
    # wrapper = FileWrapper(open(img.image.path, encoding='utf-8'))  # img.file returns full path to the image
    # print(wrapper)
    # content_type = mimetypes.guess_type(img.image.path)[0]  # Use mimetypes to get file type
    # print(content_type)
    # # response = HttpResponse(wrapper, content_type=content_type)
    # # print(response)
    # # response['Content-Length'] = os.path.getsize(img.image)
    # # response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % img.name
    # # return response
    # response = HttpResponse(wrapper, content_type='application/zip')
    # response['Content-Disposition'] = 'attachment; filename=myfile.zip'
    # return response
    image = img.image.name.split('/')[-1]
    response = HttpResponse(img.image, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename=%s' % image

    return response
