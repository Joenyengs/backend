# Generated by Django 5.2 on 2025-06-22 23:49

import datetime
import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_rename_debut_sessionyear_debut_session_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilcandidat',
            name='date_de_naissance',
            field=models.DateField(blank=True, default=datetime.datetime(2025, 6, 22, 23, 49, 18, 869423, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AlterField(
            model_name='profilcandidat',
            name='photo',
            field=models.FileField(blank=True, default='<function ProfilCandidat.user_photo_path at 0x0000025CB7AB0680>/default.jpg', max_length=255, null=True, upload_to=users.models.ProfilCandidat.user_photo_path),
        ),
    ]
