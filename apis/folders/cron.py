from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from .models import Folders
from apis.images.models import Images
from datetime import datetime
from utils.constants import TRASH_TIME
from ..folders.views import delete_multiple_folder, delete_folder

def trash_folder():
    now = datetime.now()
    try:
        trashed_folders = Folders.objects.filter(is_trashed=True)
    except ObjectDoesNotExist:
        print("there are not any trashed folders")
    for folder in trashed_folders:
        days_difference = now.date() - folder.trashed_at.date()
        if days_difference.days > TRASH_TIME:
            try:
                folder.delete()
            except ProtectedError:
                error_message = "This image {} can't be deleted!!".format(image.id)
                print(error_message)

def delete_folder_in_trash(folder):
    sub_folders = Folders.objects.filter(parent_id=folder.id)
    for sub_folder in sub_folders:
        sub_folder.delete()
    images = Images.objects.filter(folder_id=folder.id)
    for image in images:
        image.detele()
    folder.delete()

