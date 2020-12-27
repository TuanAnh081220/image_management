from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserLoginSerializer, MyTokenObtainPairSerializer

from apis.users.models import Users, PendingUsers


# Create your views here.

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        return JsonResponse({
            'message': 'Register successful!'
        }, status=status.HTTP_201_CREATED)

    else:
        return JsonResponse({
            'error_message': 'This email has already exist!',
            'errors_code': 400,
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    print(request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        print(serializer.validated_data['email'])
        print(serializer.validated_data['password'])
        user = Users.objects.get(email=email, password=password)
        if user.is_blocked:
            return JsonResponse({
                'message': "User's blocked"
            }, status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                PendingUsers.Objects.get(user_name=user.user_name)
            except ObjectDoesNotExist:
                pass
            else:
                return JsonResponse({
                    'message': 'User has not been verified'
                }, status=status.HTTP_403_FORBIDDEN)
        if user:
            refresh = MyTokenObtainPairSerializer.get_token(user)
            data = {
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
                'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response({
            'error_message': 'Email or password is incorrect!',
            'error_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    print("something here")
    return JsonResponse({
        'message': 'invalid user_name or password'
    }, status=status.HTTP_400_BAD_REQUEST)
