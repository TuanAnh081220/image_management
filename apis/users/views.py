from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Users
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Users.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def example_view(request, format=None):
    print(request.headers)
    content = {
        'status': 'request was permitted'
    }
    return Response(content)
