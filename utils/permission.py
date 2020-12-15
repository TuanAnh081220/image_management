from rest_framework.permissions import BasePermission
from .jwt import get_jwt_payload


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        payload = get_jwt_payload(request)
        return payload['is_admin']
