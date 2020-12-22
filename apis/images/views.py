import io

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from utils.user import get_user_id_from_jwt
from utils.serializers import MultiplIDsSerializer
from .serializers import UploadImagesSerializer, DetailedImageSerializer, ImageSerializer, RemoveImageTagSerializer
from .models import Images
from apis.users.views import get_user_from_id
from apis.tags.serializers import TagSerializer

from datetime import datetime

import magic

from ..tags.models import Tags, Images_Tags
from ..tags.serializers import SetImageTagSerializer


class ImagesList(generics.ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['star']
    search_fields = ['title']

    def get_queryset(self):
        user_id = get_user_id_from_jwt(self.request)
        return Images.objects.filter(is_trashed=False, owner_id=user_id).order_by('-updated_at')


@api_view(['POST'])
#@permission_classes([IsAuthenticated])
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

    fs = FileSystemStorage()
    for img in request.FILES.getlist('images'):
        title = img.name
        if is_image_title_duplicate(owner_id, title):
            title = title + "_duplicate"
        img_name = fs.save(title, img)
        img_url = fs.url(img_name)
        new_img = Images.objects.create(
            owner=owner,
            folder_id=folder_id,
            path=img_url,
            thumbnail_path=img_url,
            size=img.size,
            title=title
        )
        print(new_img.id)
    return JsonResponse({
        'message': 'successfully uploaded'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def get_detailed_image(request, image_id):
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    user_id = get_user_id_from_jwt(request)

    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = DetailedImageSerializer(instance=image)

    tag = Tags.objects.raw("select id from tags where id in (select tag_id from images_tags where image_id = 1)")

    tag_serializer = TagSerializer(tag, many=True)

    data = serializer.data
    data['tags'] = tag_serializer.data

    return JsonResponse({
        'image': data
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
    }, status=status.HTTP_400_BAD_REQUEST)


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
    image.delete()
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
        image.delete()
    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def star_image(request, image_id):
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    user_id = get_user_id_from_jwt(request)
    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    image = change_image_star_status(image, True)
    return JsonResponse({
        'image_id': image.id,
        'star': image.star
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def un_star_image(request, image_id):
    image = get_image_by_id(image_id)
    if image is None:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    user_id = get_user_id_from_jwt(request)
    if not is_owner(image.owner.id, user_id):
        return JsonResponse({
            'message': "permission denied"
        }, status=status.HTTP_403_FORBIDDEN)

    image = change_image_star_status(image, False)
    return JsonResponse({
        'image_id': image.id,
        'star': image.star
    }, status=status.HTTP_400_BAD_REQUEST)


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
def set_image_tag(request, image_id):
    serializer = SetImageTagSerializer(data=request.data)
    image = get_image_by_id(image_id)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    tag_id = serializer.data['tag_id']
    try:
        Tags.objects.get(id=tag_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'Tag does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
    try:
        Images_Tags.objects.get(image_id=image_id, tag_id=tag_id)
    except ObjectDoesNotExist:
        Images_Tags.objects.create(image=image, tag_id=tag_id)
        return JsonResponse({
            'message': 'Tag added'
        }, status=status.HTTP_200_OK)
    return JsonResponse({
        'message': "Image already had this tag"
    }, status=status.HTTP_404_NOT_FOUND)


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