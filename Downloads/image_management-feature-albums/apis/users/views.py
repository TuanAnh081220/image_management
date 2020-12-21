from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from .models import Users, PendingUsers
from .serializers import UserSerializer, DetailedUserSerializer, PendingUserSerializer, UpdateDetailedUserSerializer
from rest_framework.permissions import IsAuthenticated
from utils.permission import IsAdmin
from utils.user import get_user_id_from_jwt


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_admin', 'is_blocked']
    search_fields = ['email', 'username']


class UserUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Users.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detailed_user(request):
    user_id = get_user_id_from_jwt(request)
    try:
        user = Users.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'User does not exist!'
        }, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedUserSerializer(instance=user)
    return JsonResponse({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_detailed_user(request):
    user_id = get_user_id_from_jwt(request)
    try:
        user = Users.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'User does not exist!'
        }, status=status.HTTP_404_NOT_FOUND)
    serializer = UpdateDetailedUserSerializer(user, data=request.data)
    if not serializer.is_valid():
        return JsonResponse({
            'message': 'invalid update'
        }, status=status.HTTP_400_BAD_REQUEST)
    updated_user = serializer.save()
    return Response({
        'user_id': updated_user.id
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def verify_user(request, pending_user_id):
    try:
        pending_user = PendingUsers.objects.get(id=pending_user_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'Pending user does not exist!'
        }, status=status.HTTP_404_NOT_FOUND)
    try:
        new_user = Users.objects.create(
            user_name=pending_user.user_name,
            email=pending_user.email,
            password=pending_user.password,
        )
    except Exception:
        return JsonResponse({
            'message': 'This user is already existed!'
        }, status=status.HTTP_400_BAD_REQUEST)
    pending_user.delete()
    return JsonResponse({
        'user_id': new_user.id
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def block_user(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'User does not exist!'
        }, status=status.HTTP_404_NOT_FOUND)
    user.is_blocked = True
    user.save()
    return JsonResponse({
        'user_id': user.id,
        'is_blocked': user.is_blocked
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def un_block_user(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'User does not exist!'
        }, status=status.HTTP_404_NOT_FOUND)
    user.is_blocked = False
    user.save()
    return JsonResponse({
        'user_id': user.id,
        'is_blocked': user.is_blocked
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def example_view(request):
    content = {
        'status': 'request was permitted'
    }
    return Response(content)


def get_user_from_id(user_id):
    try:
        user = Users.objects.get(id=user_id)
        return user
    except ObjectDoesNotExist:
        return ObjectDoesNotExist
