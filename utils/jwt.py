from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend


def get_jwt_payload(request):
    jwt_object = JWTAuthentication()
    header = jwt_object.get_header(request)
    raw_token = jwt_object.get_raw_token(header)
    validated_token = jwt_object.get_validated_token(raw_token)
    token_backend = TokenBackend(algorithm='HS256')
    payload = token_backend.decode(token=str(validated_token), verify=False)
    return payload
