# Generated by Django 5.0.7 on 2024-08-04 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_object_file_object_material'),
    ]

    operations = [
        migrations.AlterField(
            model_name='texture',
            name='object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.object'),
        ),
    ]
