# Generated by Django 5.1.3 on 2025-03-14 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0012_delete_quejas'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarios',
            name='refresh_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]
