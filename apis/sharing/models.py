from django.db import models

# Create your models here.
from apis.folders.models import Folders
from apis.images.models import Images
from apis.users.models import Users


class Shared_Images(models.Model):
    image = models.ForeignKey(Images, on_delete=models.CASCADE)
    shared_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'shared_images'


class Shared_Folders(models.Model):
    folder = models.ForeignKey(Folders, on_delete=models.CASCADE)
    shared_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'shared_folders'