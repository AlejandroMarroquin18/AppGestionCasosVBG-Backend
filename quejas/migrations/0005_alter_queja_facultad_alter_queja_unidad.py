# Generated by Django 5.1.3 on 2025-01-31 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quejas', '0004_merge_20250131_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queja',
            name='facultad',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='queja',
            name='unidad',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
