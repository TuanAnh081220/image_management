from django.urls import path
from . import views

urlpatterns = [
    path('<int:image_id>/sharing', views.share_image, name="sharing_image"),
    path('shared', views.get_shared_image, name="shared_images")
]