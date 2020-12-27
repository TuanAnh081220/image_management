# Generated by Django 3.1.3 on 2020-12-27 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='avatar_url',
        ),
        migrations.AddField(
            model_name='users',
            name='avatar',
            field=models.ImageField(null=True, upload_to='profile_picture'),
        ),
    ]
