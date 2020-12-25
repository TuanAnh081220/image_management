# Generated by Django 3.1.3 on 2020-12-25 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=45)),
                ('path', models.CharField(max_length=2000)),
                ('thumbnail_path', models.CharField(max_length=2000)),
                ('folder_id', models.IntegerField()),
                ('star', models.BooleanField(default=False)),
                ('size', models.IntegerField()),
                ('is_trashed', models.BooleanField(default=False)),
                ('trashed_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('publicity', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'images',
            },
        ),
    ]
