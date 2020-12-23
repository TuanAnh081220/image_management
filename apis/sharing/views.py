import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apis.images.models import Images
from apis.images.serializers import ShareImageSerializer
from apis.sharing.models import Shared_Images
from apis.users.models import Users
from utils.user import get_user_id_from_jwt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_image(request, image_id):
    owner_id = get_user_id_from_jwt(request)
    try:
        Images.objects.get(id=image_id, owner_id = owner_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'Image not found'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ShareImageSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'Invalid'
        }, status=status.HTTP_400_BAD_REQUEST)
    user_id = serializer.data['user_id']
    try:
        Users.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    created_at = datetime.now()
    updated_at = datetime.now()
    Shared_Images.objects.create(image_id=image_id, user_id=user_id,
                                 created_at=created_at, updated_at=updated_at)
    return JsonResponse({
        'message': 'Image shared'
    }, status=status.HTTP_200_OK)