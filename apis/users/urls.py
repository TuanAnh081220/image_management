from django.urls import path
from .views import UsersViewSet, example_view, get_detailed_user, update_detailed_user, verify_user, block_user, \
    un_block_user, upload_avatar

urlpatterns = [
    path('', UsersViewSet.as_view({'get': 'list'}), name="users_view_and_retrieve"),
    path('<int:pk>', UsersViewSet.as_view({'get': 'retrieve'}), name="retrieve user"),
    path('example', example_view, name="example_view"),
    path('me', get_detailed_user, name="get_detailed_user"),
    path('me/update', update_detailed_user, name="update_detailed_user"),
    path('<int:pending_user_id>/verify', verify_user, name="verify_user"),
    path('<int:user_id>/block', block_user, name="block_user"),
    path('<int:user_id>/unblock', un_block_user, name="un_block_user"),
    path('avatar', upload_avatar, name="upload_avatar")
]
