# Generated by Django 3.1.3 on 2020-12-22 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_auto_20201223_0438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='images',
            old_name='folder',
            new_name='folder_id',
        ),
    ]
