from django.urls import path

from .views import FoldersListTrash, FoldersList, \
    create_folder, \
    get_detailed_folder, \
    trash_folder, \
    restore_folder, \
    delete_folder, \
    update_folder, \
    trash_multiple_folder, \
    restore_multiple_folder, \
    delete_multiple_folder, get_folder_list

urlpatterns = [
    path('list', FoldersList.as_view(), name="list_folders"),
    path('list/trash', FoldersListTrash.as_view(), name="list_folders"),
    path('create', create_folder, name="create_folder"),
    path('<int:folder_id>/detail', get_detailed_folder, name="get_detailed_folder"),
    path('<int:folder_id>/trash', trash_folder, name="trash_folder"),
    path('<int:folder_id>/restore', restore_folder, name="restore_folder"),
    path('<int:folder_id>/delete', delete_folder, name="delete_folder"),
    # used for update folder's title and change parent_id of folder
    path('<int:folder_id>/update', update_folder, name="update_folder"),
    path('trash', trash_multiple_folder, name="trash_multiple_folder"),
    path('delete', delete_multiple_folder, name="delete_multiple_folder"),
    path('restore', restore_multiple_folder, name="restore_multiple_folder"),
]
