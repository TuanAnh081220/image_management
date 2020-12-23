from django.db import models

# Create your models here.
class Shared_Images(models.Model):
    image = models.ForeignKey(Images, on_delete=models.CASCADE)
    shared_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'shared_images'