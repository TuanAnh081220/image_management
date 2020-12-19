from django.urls import path

from .views import FoldersList, \
    create_folder, \
    get_detailed_folder

urlpatterns = [
    path('', FoldersList.as_view(), name="list_folders"),
    path('create', create_folder, name="create_folder"),
    path('<int:folder_id>/detail', get_detailed_folder, name="get_detailed_folder")
]