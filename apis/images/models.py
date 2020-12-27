from django.db import models

from apis.users.models import Users

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# Create your models here.

class Images(models.Model):
    title = models.CharField(max_length=45, null=False)
    image = models.ImageField(null=False)
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(50, 50)],
                               format='JPEG',
                               options={'quality': 60})
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, null=False)
    folder_id = models.IntegerField()
    star = models.BooleanField(default=False, null=False)
    size = models.IntegerField(null=False)
    is_trashed = models.BooleanField(default=False, null=False)
    trashed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    publicity = models.BooleanField(default=False, null=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'images'
