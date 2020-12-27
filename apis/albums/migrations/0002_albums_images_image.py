# Generated by Django 3.1.3 on 2020-12-27 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('albums', '0001_initial'),
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='albums_images',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.images'),
        ),
    ]
