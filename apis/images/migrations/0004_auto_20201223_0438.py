# Generated by Django 3.1.3 on 2020-12-22 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20201223_0429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='folder',
            field=models.IntegerField(),
        ),
    ]
