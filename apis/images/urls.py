from django.urls import path

from .views import test_upload_image_view, ImagesList, upload_image, \
    get_detailed_image, \
    trash_image, \
    restore_image, \
    trash_multiple_image, \
    delete_multiple_image, \
    restore_multiple_image, \
    star_image, \
    un_star_image, \
    set_image_tag, \
    remove_image_tag

urlpatterns = [
    path('', ImagesList.as_view(), name="list_images"),
    path('upload', upload_image, name="test_upload_image_view"),
    path('<int:image_id>/detail', get_detailed_image, name="get_detailed_image"),
    path('<int:image_id>/trash', trash_image, name="trash_image"),
    path('<int:image_id>/restore', restore_image, name="restore_image"),
    path('trash', trash_multiple_image, name="trash_multiple_image"),
    path('delete', delete_multiple_image, name="delete_multiple_image"),
    path('restore', restore_multiple_image, name="restore_multiple_image"),
    path('<int:image_id>/like', star_image, name="star_image"),
    path('<int:image_id>/dislike', un_star_image, name="un_star_image"),
    path('<int:image_id>/tag', set_image_tag, name="set_image_tag"),
    path('<int:image_id>/un_tag', remove_image_tag, name="remove_image_tag"),
]
