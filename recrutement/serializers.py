from rest_framework import serializers
from .models import Candidature, QuizAnswer, Recours, RecoursActionHistory, TrainingModule, QuizQuestion, Traitement

class CandidatureAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = ('cv', 'lettre_motivation', 'piece_identite', 'aptitude_physique', 'diplome')
        read_only_fields = ['titre','statut', 'date_creation', 'date_modification', 'candidat','commentaire_admin']


class ListeCandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = '__all__'


class CandidatureFrontendSerializer(serializers.ModelSerializer):
    candidat = serializers.SerializerMethodField()
    formation = serializers.SerializerMethodField()
    filiere = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    dateDepot = serializers.DateTimeField(source='date_creation')
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Candidature
        fields = [
            'id', 'titre', 'commentaire_admin', 'candidat', 'formation', 'filiere',
            'statut', 'dateDepot', 'province', 'documents'
        ]

    def get_candidat(self, obj):
        user = obj.candidat
        profil = getattr(user, 'profil_candidat', None)
        return {
            "nom": getattr(profil, 'nom', '') if profil else getattr(user, 'last_name', ''),
            "prenom": getattr(profil, 'prenom', '') if profil else getattr(user, 'first_name', ''),
            "email": user.email,
            "telephone": getattr(user, 'telephone', ''),
            "genre": getattr(profil, 'genre', ''),
        }

    def get_formation(self, obj):
        profil = getattr(obj.candidat, 'profil_candidat', None)
        return getattr(profil, 'niveau_etude', '') if profil else ''

    def get_filiere(self, obj):
        profil = getattr(obj.candidat, 'profil_candidat', None)
        return getattr(profil, 'domaine_etude', '') if profil else ''

    def get_province(self, obj):
        profil = getattr(obj.candidat, 'profil_candidat', None)
        return getattr(profil, 'province_de_residence', '') if profil else ''
    
    def get_statut(self, obj):
        return obj.statut

    def get_documents(self, obj):
        """Récupère les documents associés à la candidature."""
        # Définir les champs et leurs libellés
        doc_fields = [
            ("cv", "CV"),
            ("lettre_motivation", "Lettre de motivation"),
            ("diplome", "Diplôme"),
            ("aptitude_physique", "Aptitude physique"),
            ("piece_identite", "Pièce d'identité"),
        ]
        docs = []
        # Parcourir les champs et récupérer les URLs
        # des fichiers si disponibles
        for idx, (field, label) in enumerate(doc_fields, start=1):
            file_field = getattr(obj, field, None)
            if file_field:
                url = file_field.url if hasattr(file_field, 'url') else ""
            docs.append({
                "id": idx,
                "nom": label,
                "type": field,
                "url": url,
                "statut": obj.statut,
            })
        return docs


class CandidatureStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = '__all__'
        read_only_fields = ['titre','statut', 'date_creation', 'date_modification', 'candidat','commentaire_admin']


class TraiterCandidatureSerializer(serializers.ModelSerializer):
    cv_url = serializers.SerializerMethodField()
    lettre_de_motivation_url = serializers.SerializerMethodField()
    piece_identite_url = serializers.SerializerMethodField()
    aptitude_physique_url = serializers.SerializerMethodField()
    titre_academique_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidature
        fields = [
            'statut','commentaire_admin','id', 'cv_url', 'lettre_de_motivation_url', 
            'piece_identite_url', 'aptitude_physique_url', 'titre_academique_url'
        ]

    def get_cv_url(self, obj):
        return obj.cv.url if obj.cv else None

    def get_lettre_de_motivation_url(self, obj):
        return obj.lettre_motivation.url if obj.lettre_motivation else None

    def get_piece_identite_url(self, obj):
        return obj.piece_identite.url if obj.piece_identite else None

    def get_aptitude_physique_url(self, obj):
        return obj.aptitude_physique.url if obj.aptitude_physique else None

    def get_titre_academique_url(self, obj):
        return obj.titre_academique.url if obj.titre_academique else None


class RecoursSerializer(serializers.ModelSerializer):
    # candidat_email = serializers.SerializerMethodField(read_only=True)
    # candidat_nom_complet = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recours
        fields = '__all__'
        read_only_fields = ['date_soumission', 'traite_par', 'date_traitement', 'commentaire_admin', 'traite','candidature']    #'candidat_email', 'candidat_nom_complet',

    def get_candidat_email(self, obj):
        return getattr(obj.candidature.candidat, 'email', None)

    def get_candidat_nom_complet(self, obj):
        user = obj.candidature.candidat
        return f"{user.first_name} {user.last_name}".strip() if user else None


class RecoursStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recours
        fields = ['traite', 'commentaire_admin']


class RecoursActionHistorySerializer(serializers.ModelSerializer):
    admin_email = serializers.CharField(source='admin.email', read_only=True)
    class Meta:
        model = RecoursActionHistory
        fields = ['id', 'action', 'commentaire', 'date_action', 'admin_email']

############################## QUIZ ###############################
class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = '__all__'


class TrainingModuleSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingModule
        fields = ['id', 'title', 'description', 'content', 'questions']


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ['id', 'user', 'question', 'selected_option', 'is_correct', 'answered_at']
        read_only_fields = ['user', 'is_correct', 'answered_at']

    def create(self, validated_data):
        question = validated_data['question']
        selected_option = validated_data['selected_option']
        is_correct = (selected_option == question.correct_option)
        validated_data['is_correct'] = is_correct
        return super().create(validated_data)
    

class TraitementSerializer(serializers.ModelSerializer):
    # evaluateur_email = serializers.EmailField(source='evaluateur.email', read_only=True)
    class Meta:
        model = Traitement
        fields = ['cv', 'lettre_de_motivation', 'piece_identite', 'aptitude_physique', 'titre_academique', 'observations' ]
    
class TraitementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traitement
        fields = ['cv', 'lettre_de_motivation', 'piece_identite', 'aptitude_physique', 'titre_academique', 'observations' ]
    
    def get_candidature(self, obj):
        candidature = obj.candidature
        profil = getattr(candidature, 'traitements', None)
        return {
            "Titre": getattr(profil, 'titre', '') if profil else getattr(candidature, 'titre', ''),
            "Observations": getattr(profil, 'commentaire_admin', '') if profil else getattr(candidature, 'commentaire_admin', ''),
        }
    
class TraitementWithCandidatureSerializer(serializers.ModelSerializer):
    candidature = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Traitement
        fields = ['cv', 'lettre_de_motivation', 'piece_identite', 'aptitude_physique', 'titre_academique', 'observations', 'candidature']
