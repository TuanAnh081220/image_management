from django.urls import path
from . import views

urlpatterns = [
    path('list', views.tag_list, name="tag-list"),
    path('detail/<int:tag_id>', views.tag_detail, name="tag-detail"),
    path('create', views.tag_create, name="tag-create"),
]