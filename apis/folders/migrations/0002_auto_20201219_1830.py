# Generated by Django 3.1.3 on 2020-12-19 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('folders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='folders',
            name='is_trashed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='folders',
            name='trashed_at',
            field=models.DateTimeField(null=True),
        ),
    ]