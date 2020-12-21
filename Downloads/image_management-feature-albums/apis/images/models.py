from django.db import models

from apis.users.models import Users


# Create your models here.

class Images(models.Model):
    title = models.CharField(max_length=45, null=False)
    path = models.CharField(max_length=2000, null=False)
    thumbnail_path = models.CharField(max_length=2000, null=False)
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, null=False)
    folder_id = models.IntegerField(default=0)
    star = models.BooleanField(default=False, null=False)
    size = models.IntegerField(null=False)
    is_trashed = models.BooleanField(default=False, null=False)
    trashed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'images'
