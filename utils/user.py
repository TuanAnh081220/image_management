from .jwt import get_jwt_payload


def get_user_id_from_jwt(request):
    payload = get_jwt_payload(request)
    return payload['user_id']
