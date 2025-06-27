from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import CustomUser
from .models import Candidature, Recours
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

###Ce test utilise APIClient de DRF pour simuler des requêtes authentifiées 
# sur l’endpoint /api/candidatures/ pour valider : 
# (1)l'accès restreint des utilisateurs à leurs propres candidatures, et 
# (2)l'accès complet pour un administrateur

class CandidatureAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@test.com', password='test123', username='user1')
        self.user2 = User.objects.create_user(email='user2@test.com', password='test123', username='user2')
        self.admin = User.objects.create_superuser(email='admin@test.com', password='admin123', username='admin', role='admin')
        
        # Créer des candidatures pour les utilisateurs
        Candidature.objects.create(
            candidat=self.user1, titre='Test A',
            lettre_motivation=SimpleUploadedFile('motivation.pdf', b'dummy file content', content_type='application/pdf'),
            cv=SimpleUploadedFile('cv.pdf', b'dummy file content', content_type='application/pdf'),
            diplome=SimpleUploadedFile('diplome.pdf', b'dummy file content', content_type='application/pdf'),
            aptitude_physique=SimpleUploadedFile('aptitude.pdf', b'dummy file content', content_type='application/pdf'),
            piece_identite=SimpleUploadedFile('identite.pdf', b'dummy file content', content_type='application/pdf')
        )
        Candidature.objects.create(
            candidat=self.user2, titre='Test B',
            lettre_motivation=SimpleUploadedFile('motivation.pdf', b'dummy file content', content_type='application/pdf'),
            cv=SimpleUploadedFile('cv.pdf', b'dummy file content', content_type='application/pdf'),
            diplome=SimpleUploadedFile('diplome.pdf', b'dummy file content', content_type='application/pdf'),
            aptitude_physique=SimpleUploadedFile('aptitude.pdf', b'dummy file content', content_type='application/pdf'),
            piece_identite=SimpleUploadedFile('identite.pdf', b'dummy file content', content_type='application/pdf')
        )

    def test_user_only_sees_their_candidatures(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/recrutement/candidatures/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titre'], 'Test A')

    def test_admin_sees_all_candidatures(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/recrutement/candidatures/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

class CandidatureCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='candidat@test.com', password='test123', username='candidat1', role='candidat')
        self.client.force_authenticate(user=self.user)

    # def test_create_candidature(self):
    #     data = {
    #         'titre': 'Dossier ENA',
    #         'lettre_motivation': SimpleUploadedFile('motivation.pdf', b'dummy file content', content_type='application/pdf'),
    #         'cv': SimpleUploadedFile('cv.pdf', b'dummy file content', content_type='application/pdf'),
    #         'diplome': SimpleUploadedFile('diplome.pdf', b'dummy file content', content_type='application/pdf'),
    #         'aptitude_physique': SimpleUploadedFile('aptitude.pdf', b'dummy file content', content_type='application/pdf'),
    #         'piece_identite': SimpleUploadedFile('identite.pdf', b'dummy file content', content_type='application/pdf'),
    #     }

    #     response = self.client.post('/api/recrutement/candidatures/', data, format='multipart')
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(Candidature.objects.count(), 1)
    #     self.assertEqual(Candidature.objects.first().titre, 'Dossier ENA')
    #     self.assertEqual(Candidature.objects.first().candidat, self.user)
    #     # Vérifie le statut initial si défini dans le modèle
    #     self.assertEqual(getattr(Candidature.objects.first(), 'statut', 'non_envoye'), 'non_envoye')

# class RecoursCreateTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(email='candidat@test.com', password='test123', username='candidat1', role='candidat')
#         self.client.force_authenticate(user=self.user)
#         self.candidature = Candidature.objects.create(
#             candidat=self.user,
#             titre='Candidature refusée',
#             lettre_motivation=SimpleUploadedFile('motivation.pdf', b'dummy file content', content_type='application/pdf'),
#             cv=SimpleUploadedFile('cv.pdf', b'dummy file content', content_type='application/pdf'),
#             diplome=SimpleUploadedFile('diplome.pdf', b'dummy file content', content_type='application/pdf'),
#             aptitude_physique=SimpleUploadedFile('aptitude.pdf', b'dummy file content', content_type='application/pdf'),
#             piece_identite=SimpleUploadedFile('identite.pdf', b'dummy file content', content_type='application/pdf'),
#             statut='rejete'
#         )

    # def test_create_recours(self):
    #     data = {
    #         'candidature': self.candidature.id,
    #         'motif_rejet': 'Non conforme',
    #         'justification': "Erreur d’interprétation",
    #         'document_justificatif': SimpleUploadedFile('preuve.pdf', b'preuve', content_type='application/pdf')
    #     }

    #     response = self.client.post('/api/recrutement/recours/', data, format='multipart')
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(Recours.objects.count(), 1)
    #     self.assertEqual(Recours.objects.first().candidature, self.candidature)