from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from .models import Folders
from apis.images.models import Images
from datetime import datetime
from utils.constants import TRASH_TIME


def trash_image():
    now = datetime.now()
    try:
        trashed_folders = Folders.objects.filter(is_trashed=True)
    except ObjectDoesNotExist:
        print("there are not any trashed folders")
    try:
        images = Images.objects.filter(is_trashed=True, folder_id=0)
    except ObjectDoesNotExist:
        print("there are not any trashed images")
    for image in images:
        days_difference = now.date() - image.trashed_at.date()
        if days_difference.days > TRASH_TIME:
            try:
                image.delete()
            except ProtectedError:
                error_message = "This image {} can't be deleted!!".format(image.id)
                print(error_message)
