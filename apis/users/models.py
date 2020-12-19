from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class Users(AbstractUser, models.Model):
    username = None
    is_staff = None
    is_superuser = None
    first_name = None
    last_name = None
    date_joined = None

    user_name = models.CharField(max_length=45, null=False, default="default user name")
    email = models.CharField(max_length=45, unique=True, null=False)
    password = models.CharField(max_length=45, null=False)
    is_admin = models.BooleanField(default=False, null=False)
    avatar_url = models.CharField(max_length=2000)
    is_blocked = models.BooleanField(default=False, null=False)
    last_login = models.DateTimeField(auto_now_add=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = 'users'


class PendingUsers(models.Model):
    user_name = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    password = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_name + " " + self.email

    class Meta:
        db_table = 'pending_users'
