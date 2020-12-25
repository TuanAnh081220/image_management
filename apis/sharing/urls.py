from django.urls import path
from . import views

urlpatterns = [
    path('images/sharing', views.share_image, name="sharing_images"),
    path('images/shared', views.get_all_shared_image, name="shared_images"),
    path('images/shared/detail', views.get_shared_image_detail, name="shared_images_detail"),
    path('folders/sharing', views.share_folder, name="sharing_folders"),
    path('folders/shared', views.get_all_shared_folders, name="shared_folders"),
    path('folders/shared/detail', views.get_shared_folder_detail, name="shared_folder_detail")
]