from django.db import models
from apis.users.models import Users
from apis.images.models import Images

# Create your models here.
class Tags(models.Model):
    name = models.CharField(max_length=45, null=False)
    owner = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tags'

class Images_Tags(models.Model):
    image = models.ForeignKey(Images, on_delete=models.CASCADE, related_name="image_tag")
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, related_name="tag_image")

    class Meta:
        db_table = 'images_tags'