from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from .models import Images
from datetime import datetime
from utils.constants import TRASH_TIME
from apis.albums.models import Albums_Images
from apis.tags.models import Images_Tags
from apis.sharing.models import Shared_Images

def trash_image():
    now = datetime.now()
    try:
        images = Images.objects.filter(is_trashed=True)
    except ObjectDoesNotExist:
        print("there are not any trashed images")
    print("execute here")
    for image in images:
        # days_difference = now - image.trashed_at
        print(now)
        print(image.trashed_at)
        print(image.id)
        if days_difference.days > TRASH_TIME:
            try:
                Albums_Images.objects.get(image_id=image.id).delete()
            except ObjectDoesNotExist:
                print("This image {} does not exist in album!".format(image.id))
            try:
                Images_Tags.objects.get(image_id=image.id).delete()
            except ObjectDoesNotExist:
                print("This image {} does not have tag!".format(image.id))
            try:
                Shared_Images.objects.get(image_id=image.id).delete()
            except ObjectDoesNotExist:
                print("This image {} is not shared!".format(image.id))
            try:
                image.delete()
            except ObjectDoesNotExist:
                print("This image {} does not exist!".format(image.id))
            except ProtectedError:
                error_message = "This image {} can't be deleted!!".format(image.id)
                print(error_message)

