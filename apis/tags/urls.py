from django.urls import path
from . import views

urlpatterns = [
    path('', views.TagsList.as_view(), name="tag-list"),
    path('detail/<int:tag_id>', views.tag_detail, name="tag-detail"),
    path('create', views.tag_create, name="tag-create"),
]