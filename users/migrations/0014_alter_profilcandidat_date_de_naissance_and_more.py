# Generated by Django 5.2 on 2025-06-15 08:50

import datetime
import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_profilcandidat_date_de_naissance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilcandidat',
            name='date_de_naissance',
            field=models.DateField(blank=True, default=datetime.datetime(2025, 6, 15, 8, 49, 58, 28615, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AlterField(
            model_name='profilcandidat',
            name='photo',
            field=models.FileField(blank=True, default='<function ProfilCandidat.user_photo_path at 0x0000019FE6AAC720>/default.jpg', max_length=255, null=True, upload_to=users.models.ProfilCandidat.user_photo_path),
        ),
    ]
