# Generated by Django 5.2 on 2025-06-05 15:58

import recrutement.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidature',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('titre', models.CharField(max_length=255)),
                ('lettre_motivation', models.FileField(upload_to=recrutement.models.Candidature.candidature_upload_path)),
                ('cv', models.FileField(upload_to=recrutement.models.Candidature.candidature_upload_path)),
                ('diplome', models.FileField(upload_to=recrutement.models.Candidature.candidature_upload_path)),
                ('aptitude_physique', models.FileField(upload_to=recrutement.models.Candidature.candidature_upload_path)),
                ('piece_identite', models.FileField(upload_to=recrutement.models.Candidature.candidature_upload_path)),
                ('statut', models.CharField(choices=[('envoye', 'Envoyée'), ('en_traitement', 'En cours de traitement'), ('traite', 'Traitée'), ('valide', 'Validée'), ('rejete', 'Rejetée'), ('recours', 'Recours')], default='envoye', max_length=20)),
                ('commentaire_admin', models.TextField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizAnswer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('selected_option', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1)),
                ('is_correct', models.BooleanField()),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=500)),
                ('option_a', models.CharField(max_length=255)),
                ('option_b', models.CharField(max_length=255)),
                ('option_c', models.CharField(max_length=255)),
                ('option_d', models.CharField(max_length=255)),
                ('correct_option', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1)),
                ('explanation', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recours',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('motif_rejet', models.TextField()),
                ('justification', models.TextField()),
                ('document_justificatif', models.FileField(blank=True, null=True, upload_to=recrutement.models.Recours.recours_upload_path)),
                ('date_soumission', models.DateTimeField(auto_now_add=True)),
                ('traite', models.BooleanField(default=False)),
                ('date_traitement', models.DateTimeField(blank=True, null=True)),
                ('commentaire_admin', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Recours',
                'verbose_name_plural': 'Recours',
                'ordering': ['-date_soumission'],
            },
        ),
        migrations.CreateModel(
            name='RecoursActionHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=255)),
                ('commentaire', models.TextField(blank=True)),
                ('date_action', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrainingModule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Traitement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cv', models.CharField(choices=[('conforme', 'Conforme'), ('non_conforme', 'Non Conforme'), ('falsifie', 'Falsifié'), ('autre', 'Autre')], default='non_conforme', max_length=20)),
                ('lettre_de_motivation', models.CharField(choices=[('conforme', 'Conforme'), ('non_conforme', 'Non Conforme'), ('falsifie', 'Falsifié'), ('autre', 'Autre')], default='non_conforme', max_length=20)),
                ('piece_identite', models.CharField(choices=[('conforme', 'Conforme'), ('non_conforme', 'Non Conforme'), ('falsifie', 'Falsifié'), ('autre', 'Autre')], default='non_conforme', max_length=20)),
                ('aptitude_physique', models.CharField(choices=[('conforme', 'Conforme'), ('non_conforme', 'Non Conforme'), ('falsifie', 'Falsifié'), ('autre', 'Autre')], default='non_conforme', max_length=20)),
                ('titre_academique', models.CharField(choices=[('conforme', 'Conforme'), ('non_conforme', 'Non Conforme'), ('falsifie', 'Falsifié'), ('autre', 'Autre')], default='non_conforme', max_length=20)),
                ('observations', models.TextField(blank=True)),
                ('date_traitement', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Traitement',
                'verbose_name_plural': 'Traitements',
                'ordering': ['-date_traitement'],
            },
        ),
    ]
