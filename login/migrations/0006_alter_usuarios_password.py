# Generated by Django 5.1.3 on 2024-11-15 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_alter_usuarios_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
