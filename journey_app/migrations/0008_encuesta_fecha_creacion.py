# Generated by Django 4.1.7 on 2023-04-12 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journey_app', '0007_encuesta'),
    ]

    operations = [
        migrations.AddField(
            model_name='encuesta',
            name='fecha_creacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]