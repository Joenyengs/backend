from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .managers import CustomUserManager
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os
import uuid
# from django.db.models.fields.related import ForeignKey, OneToOneField
from django.core.validators import RegexValidator
#from dateutil.relativedelta import relativedelta

class SessionYear(models.Model):
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )
    debut_session = models.DateField()
    fin_session = models.DateField()

    debut_soumission_candidature = models.DateField(null=True)
    fin_soumission_candidature = models.DateField(null=True)

    debut_soumission_recours = models.DateField(null=True)
    fin_soumission_recours = models.DateField(null=True)
    
    promotion = models.IntegerField()
    denomination = models.CharField(max_length=30, blank=True, null=True)

    @property
    def is_current(self):
        """
        Vérifie si la session est en cours.
        """
        today = timezone.now().date()
        return self.debut_session <= today <= self.fin_session
    
    @property
    def can_submit_candidature(self):
        """
        Vérifie si la période de soumission des candidatures est en cours.
        """
        today = timezone.now().date()
        return self.debut_soumission_candidature <= today <= self.fin_soumission_candidature
    
    def __str__(self):
        return f"Promotion {self.promotion} - {self.denomination if self.denomination else 'Sans dénomination'}"


class UserRoles(models.TextChoices):
    CANDIDAT = ("candidat", "Futur élève")
    ELEVE = ("eleve", "Elève")
    ALUMNI = ("alumni", "Ancien élève")
    EVALUATEUR = ("evaluateur", "Evaluateur")
    CORRECTEUR = ("correcteur", "Correcteur")
    FORMATEUR = ("formateur", "Formateur")
    AGENT = ("agent", "Agent administratif")
    ADMIN = ("admin", "Admin")
    #EVALUATEUR2 = ("evaluateur2", "Evaluateur second niveau")


class CustomUser(AbstractUser) :
    """Modèle utilisateur personnalisé pour l'application de l'ENA-RDC."""
    
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=25, choices=UserRoles.choices, default=UserRoles.CANDIDAT)
    otp = models.CharField(max_length=6, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.username and self.first_name and self.last_name:
            self.username = f"{self.first_name}.{self.last_name}".lower()
        super().save(*args, **kwargs)

    def __repr__(self):
        return f"{self.first_name}-{self.last_name}"
    

class ProfilCandidat(models.Model):
    def user_photo_path(instance, filename):
        return os.path.join(
            'users',
            f'{instance.user.email}',
            filename
        )
    
    @property
    def photo_filename(self):
        """Returns only the filename of the photo field."""
        if self.photo:
            return os.path.basename(self.photo.name)
        return None
    
    @property
    def photo_url(self):
        """Returns the URL of the photo field."""
        if self.photo:
            return self.photo.url
        return None

    ##################################### 1. IDENTITE #####################################

    GENRES = [
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ]

    ETAT_CIVIL = [
        ('C', 'Célibataire'),
        ('M', 'Marié(e)'),
        ('V', 'Veuf(ve)'),
        ('D', 'Divorcé(e)')
    ]

    NATONALITES = [
        ('RDC', 'République Démocratique du Congo'),
        ('AUTRE', 'Autre')
    ]

    def get_first_user_id():
        first_user = CustomUser.objects.first()
        return first_user.id if first_user else None

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_candidat', null=False, blank=False, default=get_first_user_id)
    updated_at = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(SessionYear, on_delete=models.CASCADE, related_name='candidats',  blank=True, null=True)
    numero_piece_identite = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message="Ce champ n'accepte que des lettres et des chiffres.",
                code='invalid_numero_piece_identite'
            )
        ]
    )
    nom = models.CharField(max_length=50, blank=True, null=True)
    postnom = models.CharField(max_length=50, blank=True, null=True)
    prenom = models.CharField(max_length=50, blank=True, null=True)
    genre = models.CharField(max_length=1, choices=GENRES, blank=True, null=True)
    etat_civil = models.CharField(max_length=1, choices=ETAT_CIVIL, blank=True, null=True)
    lieu_de_naissance = models.CharField(max_length=50, blank=True, null=True)
    date_de_naissance = models.DateField(default=timezone.now(), blank=True, null=True)
    photo =  models.FileField(upload_to=user_photo_path, default=f'{user_photo_path}/default.jpg', blank=True, null=True, max_length=255)
    adresse_physique = models.TextField(blank=True, null=True)
    province_de_residence = models.CharField(max_length=50, blank=True, null=True)
    ville_de_residence = models.CharField(max_length=50, blank=True, null=True)
    province_d_origine = models.CharField(max_length=50, blank=True, null=True)
    nationalite = models.CharField(max_length=50, choices=NATONALITES, blank=True, null=True)

    ##################################### 2. FORMATION #####################################
    NIVEAUX_ETUDE = [
        ('doctorat', 'Doctorat'),
        ('maitrise', 'Maitrise'),
        ('licence_bac+5', 'Licence Bac+5'),
        ('licence_bac+3', 'Licence Bac+3'),
        ('graduat', 'Graduat'),
        ('diplome_etat', "Diplome d'état")
    ]

    DOMAINES_ETUDE = [
        ("Administration", "Administration"),
        ("Agronomie", "Agronomie"),
        ("Agronomie générale", "Agronomie générale"),
        ("Aménagement et gestion des ressources naturelles / Environnement", "Aménagement et gestion des ressources naturelles / Environnement"),
        ("Anthropologie", "Anthropologie"),
        ("Architecture", "Architecture"),
        ("Arts dramatiques et cinématographie", "Arts dramatiques et cinématographie"),
        ("Arts plastiques", "Arts plastiques"),
        ("Aviation civile", "Aviation civile"),
        ("Bâtiments et travaux publics", "Bâtiments et travaux publics"),
        ("Biologie médicale", "Biologie médicale"),
        ("Chimie", "Chimie"),
        ("Cinéma", "Cinéma"),
        ("Communication", "Communication"),
        ("Comptabilité", "Comptabilité"),
        ("Criminologie", "Criminologie"),
        ("Design textile, stylisme et création de mode", "Design textile, stylisme et création de mode"),
        ("Développement", "Développement"),
        ("Diplôme MITEL", "Diplôme MITEL"),
        ("Droit", "Droit"),
        ("Écologie", "Écologie"),
        ("Économie", "Économie"),
        ("Électronique", "Électronique"),
        ("Environnement et développement durable", "Environnement et développement durable"),
        ("Exploitation Aéronautique", "Exploitation Aéronautique"),
        ("Exploitation et production pétrolière", "Exploitation et production pétrolière"),
        ("Finance, Banques et Assurances", "Finance, Banques et Assurances"),
        ("Fiscalité", "Fiscalité"),
        ("Foresterie", "Foresterie"),
        ("Génie civil", "Génie civil"),
        ("Génie des mines", "Génie des mines"),
        ("Génie électrique", "Génie électrique"),
        ("Génie informatique", "Génie informatique"),
        ("Génie logiciel", "Génie logiciel"),
        ("Génie mécanique", "Génie mécanique"),
        ("Génie textile", "Génie textile"),
        ("Géographie", "Géographie"),
        ("Géologie", "Géologie"),
        ("Géotechnique et Hydrogéologie", "Géotechnique et Hydrogéologie"),
        ("Gestion de l'Environnement", "Gestion de l'Environnement"),
        ("Gestion financière", "Gestion financière"),
        ("Gestion des entreprises et organisation du travail / GRH", "Gestion des entreprises et organisation du travail / GRH"),
        ("Histoire et archivistique", "Histoire et archivistique"),
        ("Hôtellerie et tourisme", "Hôtellerie et tourisme"),
        ("Informatique", "Informatique"),
        ("Kinésithérapie", "Kinésithérapie"),
        ("Langues et littératures africaines", "Langues et littératures africaines"),
        ("Langues étrangères (français, anglais, espagnol, chinois, allemand, etc.)", "Langues étrangères (français, anglais, espagnol, chinois, allemand, etc.)"),
        ("Lettres et Sciences humaines", "Lettres et Sciences humaines"),
        ("Management des organisations", "Management des organisations"),
        ("Marketing", "Marketing"),
        ("Mathématique", "Mathématique"),
        ("Mathématique-Informatique", "Mathématique-Informatique"),
        ("Médicine", "Médicine"),
        ("Médecine générale", "Médecine générale"),
        ("Médecine vétérinaire", "Médecine vétérinaire"),
        ("Métallurgie", "Métallurgie"),
        ("Musique", "Musique"),
        ("Nutrition et technologie alimentaire", "Nutrition et technologie alimentaire"),
        ("Odontologie (chirurgie dentaire)", "Odontologie (chirurgie dentaire)"),
        ("Pêche et Aquaculture", "Pêche et Aquaculture"),
        ("Philosophie", "Philosophie"),
        ("Pharmacie", "Pharmacie"),
        ("Photographie", "Photographie"),
        ("Pédagogie", "Pédagogie"),
        ("Physique", "Physique"),
        ("Pétrole et gaz", "Pétrole et gaz"),
        ("Psychologie", "Psychologie"),
        ("Relations Internationales", "Relations Internationales"),
        ("Réseau et Télécommunications", "Réseau et Télécommunications"),
        ("Santé publique", "Santé publique"),
        ("Sciences de la communication et journalisme", "Sciences de la communication et journalisme"),
        ("Sciences de l'Éducation", "Sciences de l'Éducation"),
        ("Sciences infirmières", "Sciences infirmières"),
        ("Sciences politiques et administratives", "Sciences politiques et administratives"),
        ("Sciences et technologies de l'information", "Sciences et technologies de l'information"),
        ("Sociologie", "Sociologie"),
        ("Statistique", "Statistique"),
        ("Télécommunications", "Télécommunications"),
        ("Théâtre", "Théâtre"),
        ("Transport et logistique", "Transport et logistique"),
        ("Urbanisme", "Urbanisme"),
        ("Urbanisme et aménagement du territoire", "Urbanisme et aménagement du territoire"),
        ("Zootechnie", "Zootechnie"),
        ("Autre", "Autre"),
    ]

    # Génère une liste de floats de 60.0 à 99.9 inclus, avec un pas de 0.1
    score_choices = list(range(60, 100))
    SCORE_CHOICES = [(v, str(v)) for v in score_choices]

    def default_annee_de_graduation():
        return datetime.now().year - 25
    
    @classmethod
    def liste_niveaux_etude(cls):
        return [niveau[0] for niveau in cls.NIVEAUX_ETUDE]
    
    @property
    def liste_domaines_etude(self):
        return [domaine[0] for domaine in self.DOMAINES_ETUDE]

    niveau_etude = models.CharField(max_length=50, choices=NIVEAUX_ETUDE, blank=False, null=False)
    domaine_etude = models.CharField(max_length=100, choices=DOMAINES_ETUDE, blank=False, null=False)
    universite_frequentee = models.CharField(max_length=50, blank=True, null=True)
    score_obtenu = models.FloatField(choices=SCORE_CHOICES, blank=True, null=True, validators=[MinValueValidator(60.0), MaxValueValidator(99.9)])
    annee_de_graduation = models.IntegerField(default=default_annee_de_graduation, validators=[MinValueValidator(2013, "L'année de graduation ne peut être inférieur à celle du début de l'ENA-RDC"), MaxValueValidator(9999, "L'année ne peut dépasser 4 digits")])

    @property
    def mention(self):
        if self.score_obtenu is None:
            return None
        if self.score_obtenu < 60:
            return "Non qualifié"
        elif 60 <= self.score_obtenu < 70:
            return "Satisfaction"
        elif 70 <= self.score_obtenu < 80:
            return "Distinction"
        elif 80 <= self.score_obtenu < 90:
            return "Grande distinction"
        else:
            return "Plus grande distinction"
        
    ##################################### 3. PROFESSION #####################################
    STATUT_CHOICES = [
        ('fonctionnaire', 'Fonctionnaire'),
        ('sans_emploi', 'Sans emploi'),
        ('employe_prive', 'Employé privé')
    ]

    statut_professionnel = models.CharField(max_length=50, choices=STATUT_CHOICES, blank=True, null=True)
    matricule = models.CharField(max_length=50, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    fonction = models.CharField(max_length=50, blank=True, null=True)
    administration_d_attache = models.CharField(max_length=50, blank=True, null=True)
    ministere = models.CharField(max_length=50, blank=True, null=True)
    entreprise = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Profil Candidat"
        verbose_name_plural = "Profils Candidats"


class ProfilEleve(models.Model):
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )

    def get_first_user_id():
        first_user = CustomUser.objects.first()
        return first_user.id if first_user else None

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_eleve', null=False, blank=False, default=get_first_user_id)
    session = models.ForeignKey(SessionYear, on_delete=models.CASCADE, related_name='eleves')


class ProfilAlumni(models.Model):
    """Modèle pour le profil des anciens élèves de l'ENA-RDC."""
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )

    def get_first_user_id():
        first_user = CustomUser.objects.first()
        return first_user.id if first_user else None
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_alumni', null=False, blank=False, default=get_first_user_id)
    annee_de_graduation = models.IntegerField(
        validators=[
            MinValueValidator(2013, "L'année de graduation ne peut être inférieur à celle du début de l'ENA-RDC"), 
            MaxValueValidator(9999, "L'année ne peut dépasser 4 digits")]
    )
    emploi_actuel = models.CharField(max_length=100, blank=True, null=True)
    dispo_mentorat = models.BooleanField(default=False)
    realisations = models.CharField(max_length=250)


class ProfilFormateur(models.Model):
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )

    def get_first_user_id():
        first_user = CustomUser.objects.first()
        return first_user.id if first_user else None
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_formateur', null=False, blank=False, default=get_first_user_id)
    expertise = models.CharField(max_length=100, blank=True, null=True)
    duree_experience = models.IntegerField()
    session = models.ForeignKey(SessionYear, on_delete=models.CASCADE, related_name='formateurs')


class ProfilEvaluateur(models.Model):
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )
    
    def get_first_user_id():
        first_user = CustomUser.objects.first()
        return first_user.id if first_user else None
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_evaluateur', null=False, blank=False, default=get_first_user_id)
    expertise = models.CharField(max_length=100, blank=True, null=True)
    duree_experience = models.IntegerField()
    session = models.ForeignKey(SessionYear, on_delete=models.CASCADE, related_name='evaluateurs')

################################# Notifications ################################
class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Communiqué'),
        ('success', 'Avis au public'),
        ('error', 'Décision'),
        ('warning', 'Alerte')
    ]
    id = models.UUIDField(
        primary_key=True,  # Utilise UUID comme clé primaire
        default=uuid.uuid4,  # génère automatiquement un nouveau UUID
        editable=False  # empêche le modification manuelle
    )
    # On utilise un champ ManyToMany pour permettre à plusieurs utilisateurs de recevoir 
    # la même notification (diffusion)
    users = models.ManyToManyField(CustomUser, related_name='notifications')
    title = models.CharField(max_length=30, default="Notification")
    message = models.CharField(max_length=512)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True)  # URL vers la ressource concernée

    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}"
    
###############################################################################

class Evenement(models.Model):
    STATUT_CHOICES = [
        ("en attente", "En attente"),
        ("confirmé", "Confirmé"),
        ("programmé", "Programmé"),
    ]
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    type_evenement = models.CharField(max_length=50)  # exemple: 'épreuve écrite', 'formation'
    visible_pour = models.CharField(max_length=50, default="candidat")
    lieu = models.CharField(max_length=100, blank=True, null=True)  # Lieu de l'événement
    nombre_participants = models.PositiveIntegerField(default=0)  # Nombre de participants attendus

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="en attente"
    )  # Statut de l'événement (en attente, confirmé, programmé)

class RolePromotionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
    ]
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='promotion_requests')
    requested_role = models.CharField(max_length=25, choices=UserRoles.choices[1:], default=UserRoles.choices[1][0])  # Exclut 'candidat'
    justification = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotion_reviews'
    )
    admin_comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Demande de promotion de rôle"
        verbose_name_plural = "Demandes de promotion de rôle"

    def __str__(self):
        return f"{self.user.email} -> {self.requested_role} ({self.status})"

def profile_completion_ratio(profil):
    """
    Returns the ratio of non-null fields for a ProfilCandidat instance,
    and whether at least 3/4 of the fields are filled.
    """
    # Exclude auto fields and relations to user/session
    model = profil.__class__
    fields = [
        f for f in model._meta.get_fields()
        if (f.concrete and not f.auto_created and f.name not in ['id', 'user', 'session'])
    ]
    total_fields = len(fields)
    non_null_count = 0

    for field in fields:
        value = getattr(profil, field.name)
        if value not in [None, '', []]:
            non_null_count += 1

    ratio = non_null_count / total_fields if total_fields else 0
    is_80_percent_or_more = ratio >= 0.8
    return {
        "total_fields": total_fields,
        "filled_fields": non_null_count,
        "ratio": ratio,
        "is_80_percent_or_more": is_80_percent_or_more
    }


@receiver(pre_save, sender=ProfilCandidat)
def update_profilcandidat_updated_at(sender, instance, **kwargs):
    instance.updated_at = timezone.now()

@receiver(post_save, sender=CustomUser)
def add_user_to_group(sender, instance, created, **kwargs):
    if created or instance.role:
        role_group_map = {
            "admin": "Admin",
            "evaluateur": "Evaluateur",
            "candidat": "Candidat",
            "alumni": "Alumni",
            "formateur": "Formateur",
            "eleve": "Eleve",
        }

        group_name = role_group_map.get(instance.role)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.clear()  
            instance.groups.add(group)
