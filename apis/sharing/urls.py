from django.urls import path
from . import views

urlpatterns = [
    path('images/sharing', views.share_image, name="sharing_images"),
    path('images/shared', views.get_shared_image, name="shared_images"),
    path('folders/sharing', views.share_folder, name="sharing_folders"),
    path('folders/shared', views.get_shared_folder, name="shared_folders")
]