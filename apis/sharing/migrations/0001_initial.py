# Generated by Django 3.1.3 on 2020-12-27 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shared_Folders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'shared_folders',
            },
        ),
        migrations.CreateModel(
            name='Shared_Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='images.images')),
            ],
            options={
                'db_table': 'shared_images',
            },
        ),
    ]
