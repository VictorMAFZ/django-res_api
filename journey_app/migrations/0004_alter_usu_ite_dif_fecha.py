# Generated by Django 4.1.7 on 2023-04-03 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journey_app', '0003_alter_usu_ite_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usu_ite',
            name='dif_fecha',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
