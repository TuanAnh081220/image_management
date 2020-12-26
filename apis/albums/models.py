from django.db import models
from apis.users.models import Users
from apis.images.models import Images

# Create your models here.
class Albums(models.Model):
    title = models.CharField(max_length=45, null=False)
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, null=False)
    star = models.BooleanField(default=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "albums"
        ordering = ['title', 'updated_at', 'created_at']

class AlbumsHaveImages(models.Model):
    album = models.ForeignKey(Albums, on_delete=models.CASCADE)
    image = models.ForeignKey(Images, on_delete=models.CASCADE, primary_key=True)
    
    class Meta:
        db_table = "albums_have_images"