from django.urls import path
from . import views

urlpatterns = [
    path('tag-list/', views.tag_list, name="tag-list"),
    path('tag-detail/<str:name>/', views.tag_detail, name="tag-detail"),
    path('tag-create/', views.tag_create, name="tag-create"),
]