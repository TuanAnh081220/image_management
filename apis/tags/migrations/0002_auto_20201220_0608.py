# Generated by Django 3.1.3 on 2020-12-19 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='owner_id',
            field=models.IntegerField(),
        ),
    ]
