# Generated by Django 5.0.7 on 2024-08-03 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_url_object_file_rename_url_objectimage_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='object',
            name='file',
        ),
        migrations.RemoveField(
            model_name='object',
            name='material',
        ),
    ]
