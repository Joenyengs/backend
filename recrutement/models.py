from django.db import models
from django.conf import settings
import os
from django.core.exceptions import ValidationError
import uuid
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser, ProfilCandidat
from statistics import mean

################################# CANDIDATURES ###############################
# La candidature est un modèle qui représente une demande d'inscription à l'ENA soumise par un candidat.
class Candidature(models.Model):
    STATUT_CHOICES = [
        #('non_envoye', 'Non envoyé'),
        ('envoye', 'Envoyée'),
        ('en_traitement', 'En cours de traitement'),
        # ('traite', 'Traitée'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
        ('recours', 'Recours')
    ]

    def candidature_upload_path(instance, filename):
        return os.path.join(
            'candidatures',
            f'user_{instance.candidat.email}',
            filename
        )

    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )
    numero = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    candidat = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidatures')
    titre = models.CharField(max_length=255)
    lettre_motivation = models.FileField(upload_to=candidature_upload_path, max_length=255, null=True, blank=True)
    cv = models.FileField(upload_to=candidature_upload_path, max_length=255, null=True, blank=True)
    diplome = models.FileField(upload_to=candidature_upload_path, max_length=255, null=True, blank=True)
    aptitude_physique = models.FileField(upload_to=candidature_upload_path, max_length=255, null=True, blank=True)
    piece_identite = models.FileField(upload_to=candidature_upload_path, max_length=255, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='envoye')
    commentaire_admin = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidat.email} - {self.titre}"

    def save(self, *args, **kwargs):
        if not self.numero:
            # Récupérer l'année en cours
            annee = date.today().year
            # Si l'année est inférieure à 2013, on la considère comme 2013
            if annee < 2013:
                annee = 2013
            # Récupérer les initiales de la province d'origine
            province = getattr(self.candidat.profil_candidat, 'province_origine', None)
            if province:
                initiales = ''.join([word[0] for word in province.upper().split()])[:3]
                initiales = initiales.ljust(3, 'X')
            else:
                initiales = 'XXX'
            # Calculer le numéro d'ordre
            prefix = f"ENA{annee}{initiales}"
            last_num = (
                Candidature.objects
                .filter(numero__startswith=prefix)
                .order_by('-numero')
                .first()
            )
            if last_num and last_num.numero[-5:].isdigit():
                ordre = int(last_num.numero[-5:]) + 1
            else:
                ordre = 1
            self.numero = f"{prefix}{ordre:05d}"
        super().save(*args, **kwargs)
    
    def auto_update_statut_candidature(self):
        """
        Met à jour automatiquement le statut de la candidature selon les critères :
        - âge > 35 ans
        - niveau d'étude dans ['graduat', 'diplome_etat', 'licence_bac+3']
        - nationalité différente de Congolaise ('RDC')
        """
        candidat = self.candidat
        # Calcul de l'âge
        if candidat.profil_candidat.date_de_naissance:
            today = date.today()
            age = today.year - candidat.profil_candidat.date_de_naissance.year - (
                (today.month, today.day) < (candidat.profil_candidat.date_de_naissance.month, candidat.profil_candidat.date_de_naissance.day)
            )
        else:
            age = None

        # Vérification des critères
        if (
            ((age is not None) and 18 < age < 36) or
            (candidat.profil_candidat.niveau_etude in ['graduat', 'diplome_etat', 'licence_bac+3']) or
            (candidat.profil_candidat.nationalite != 'RDC')
        ):
            self.statut = 'rejete'
            self.save(update_fields=['statut'])
            return True  # Statut mis à jour
        return False  # Aucun changement


@receiver(post_save, sender=Candidature)
def candidature_post_save(sender, instance, created, **kwargs):

    """ Signal qui est déclenché après la sauvegarde d'une candidature.
    Il permet de mettre à jour le statut de la candidature automatiquement
    en fonction des critères définis dans la méthode auto_update_statut_candidature.
    # Si la candidature est créée, on met à jour son statut automatiquement
    # en fonction des critères définis dans la méthode auto_update_statut_candidature """

    if not instance.titre:
        instance.titre = f"Candidature - {instance.candidat.email}"
        instance.save(update_fields=["titre"])

    if created: instance.auto_update_statut_candidature()


class Traitement(models.Model):
    DECISION_CHOICES = [
        ('conforme', 'Conforme'),
        ('non_conforme', 'Non Conforme'),
        ('falsifie', 'Falsifié'),
        ('autre', 'Autre'),
    ]

    DECISION_EVAL = [
        ('ok', 'Retenue'),
        ('ko', 'Rejetée')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidature = models.ForeignKey('Candidature', on_delete=models.CASCADE, related_name='traitements')
    evaluateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='traitements_effectues')
    cv = models.CharField(max_length=20, choices=DECISION_CHOICES, default='non_conforme')
    lettre_de_motivation = models.CharField(max_length=20, choices=DECISION_CHOICES, default='non_conforme')
    piece_identite = models.CharField(max_length=20, choices=DECISION_CHOICES, default='non_conforme')
    aptitude_physique = models.CharField(max_length=20, choices=DECISION_CHOICES, default='non_conforme')
    titre_academique = models.CharField(max_length=20, choices=DECISION_CHOICES, default='non_conforme')
    observations = models.TextField(blank=True)
    date_traitement = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(max_length=2, choices=DECISION_EVAL, default='ko')

    class Meta:
        verbose_name = "Traitement"
        verbose_name_plural = "Traitements"
        ordering = ['-date_traitement']

    def __str__(self):
        return f"{self.candidature} - par {self.evaluateur}"    




################################################## RECOURS ######################################################
# Le recours est un modèle qui représente une demande de révision d'une candidature rejetée.
class Recours(models.Model):
    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('en_traitement', 'En cours de traitement'),
        ('traite', 'Traité'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    def recours_upload_path(instance, filename):
        return os.path.join(
            'recours',
            f'user_{instance.candidat.email}',
            filename
        )
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )
    candidature = models.OneToOneField(Candidature, on_delete=models.CASCADE, related_name='recours')
    motif_rejet = models.TextField()
    justification = models.TextField()
    document_justificatif = models.FileField(upload_to=recours_upload_path, null=True, blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    date_traitement = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(null=True, blank=True)
    traite_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='recours_traites')

    def clean(self):
        if Recours.objects.filter(candidature=self.candidature).exists() and not self.pk:
            raise ValidationError("Un recours a déjà été déposé pour cette candidature.")

    def save(self, *args, **kwargs):
        self.full_clean()  # trigger validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recours - {self.candidature}"
    
    class Meta:
        verbose_name = "Recours"
        verbose_name_plural = verbose_name
        ordering = ['-date_soumission']

# Historique des actions sur le recours
# Chaque fois qu'une action est effectuée sur un recours (traitement, commentaire, etc.), une entrée est ajoutée à cette table.
class RecoursActionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recours = models.ForeignKey('Recours', on_delete=models.CASCADE, related_name='actions')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)  # ex: "Traité", "Commentaire ajouté"
    commentaire = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)


#################### Training Modules and Quiz Models ######################
class TrainingModule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()  # Or use FileField for PDFs/videos
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(TrainingModule, related_name='questions', on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.question
    

class QuizAnswer(models.Model):
    def get_question_options(self):
        try:
            q = self.question
            return [
                q.option_a,
                q.option_b,
                q.option_c,
                q.option_d,
            ]
        
        except QuizQuestion.DoesNotExist:
            return []
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey('QuizQuestion', on_delete=models.CASCADE, related_name='answers')
    selected_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


@receiver(post_save, sender=Traitement)
def update_candidature_statut_on_traitement(sender, instance, created, **kwargs):
    if not created:
        return

    candidature = instance.candidature
    traitements = Traitement.objects.filter(candidature=candidature)

    # Vérifier si tous les champs documents sont "conforme"
    champs_documents = [
        "cv",
        "lettre_de_motivation",
        "piece_identite",
        "aptitude_physique",
        "titre_academique",
    ]
    # dernier_traitement = traitements.latest("date_traitement")

    # Si oui, on met la decision du traitement a "ok"
    if all(getattr(instance, champ) == "conforme" for champ in champs_documents):
        instance.decision = "ok"

    # Sinon, on met la decision du traitement a "ko"
    # en verifiant d'abord si au moins un des champs est "non_conforme" ou "falsifie"
    elif any(getattr(instance, champ) in ["non_conforme", "falsifie"] for champ in champs_documents):
        instance.decision = "ko"

    instance.save(update_fields=["decision"])

    if traitements.count() == 1:
        # Premier traitement : statut = "en_traitement"
        candidature.statut = "en_traitement"
        candidature.save(update_fields=["statut"])

    elif traitements.count() == 2:
        # Deuxième traitement : vérifier les decisions des deux traitements

        # On cree une liste pour stocker les valeurs des décisions
        # des deux traitements
        valeurs = []
        for t in traitements:
            # valeurs.extend([getattr(t, champ) for champ in champs_documents])
            valeurs.append(t.decision)
        
        # On vérifie les valeurs des décisions des deux traitements
        # Si toutes les valeurs sont "ok" => mise a jour du statut de la candidature (valide)
        if all(val == "ok" for val in valeurs):
            candidature.statut = "valide"

        # Si toutes les valeurs sont "ko" => mise a jour du statut de la candidature (rejete)
        elif all(val == "ko" for val in valeurs):
            candidature.statut = "valide"

        # sinon => la candidature retourne dans la file de traitement pour une 
        # troisieme évaluation (traitement)
        else:
            candidature.statut = "en_traitement"
        candidature.save(update_fields=["statut"])

    elif traitements.count() == 3:
        # Troisième traitement : vérifier les décisions des traitements
        valeurs = []
        for t in traitements:
            valeurs.append(t.decision)

        # On verifie les valeurs des décisions des trois traitements
        # Si les ok sont majoritaires => mise a jour du statut de la candidature (valide)
        if valeurs.count("ok") > valeurs.count("ko"):
            candidature.statut = "valide"

        # Si les ko sont majoritaires => mise a jour du statut de la candidature (rejete)
        elif valeurs.count("ko") > valeurs.count("ok"):
            candidature.statut = "rejete"

        # Sinon, on laisse le statut inchangé
        candidature.save(update_fields=["statut"])
