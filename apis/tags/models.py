from django.db import models
from apis.users.models import Users
from apis.images.models import Images

# Create your models here.
class Tags(models.Model):
    name = models.CharField(max_length=45, null=False)
    #owner_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    owner_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tags'

class Images_Tags(models.Model):
    image_id = models.ForeignKey(Images, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tags, on_delete=models.CASCADE)

