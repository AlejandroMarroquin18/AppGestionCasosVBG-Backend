# Generated by Django 5.1.3 on 2025-02-13 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('details', models.TextField()),
                ('location', models.CharField(max_length=255)),
                ('modality', models.CharField(choices=[('presencial', 'Presencial'), ('virtual', 'Virtual')], max_length=10)),
                ('slots', models.IntegerField()),
                ('facilitator', models.CharField(max_length=255)),
            ],
        ),
    ]
