from django.urls import path

from .views import AlbumsList, get_album_by_id, get_albums_filter_by_star_status, get_detailed_album, delete_album, \
    update_album_star, update_album_title, update_album_unstar, create_album, add_image_to_album, list_image_in_album

urlpatterns = [
    path('', AlbumsList.as_view(), name="list_albums"),
    path('create', create_album, name="create_album"),
    path('<int:album_id>', get_album_by_id, name="get_album"),
    path('<int:album_id>/detail', get_detailed_album, name="get_detailed_album"),
    path('<int:album_id>/delete', delete_album, name="delete_album"),
    path('<int:album_id>/like', update_album_star, name="star_album"),
    path('<int:album_id>/dislike', update_album_unstar, name="un_star_album"),
    path('<int:album_id>/rename', update_album_title, name="rename_album"),
    path('<int:album_id>/add', add_image_to_album, name="add_image_to_album"),
    path('<int:album_id>/list_images', list_image_in_album, name="list_image_in_album")
]
