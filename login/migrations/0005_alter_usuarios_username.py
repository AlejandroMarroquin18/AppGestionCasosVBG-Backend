# Generated by Django 5.1.3 on 2024-11-15 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_alter_usuarios_options_alter_usuarios_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='username',
            field=models.CharField(default='', max_length=150),
        ),
    ]
