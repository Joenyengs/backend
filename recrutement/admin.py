from django.contrib import admin
from recrutement.forms import QuizAnswerAdminForm
from .models import Candidature, Recours, QuizAnswer, TrainingModule, QuizQuestion, Traitement
from django.utils.html import format_html




@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('titre', 'candidat', 'statut', 'date_creation')
    list_filter = ('statut', 'date_creation')
    search_fields = ('titre', 'candidat__email')
    date_hierarchy = 'date_creation'
    actions = ['valider_candidatures', 'rejeter_candidatures']

    def valider_candidatures(self, request, queryset):
        queryset.update(statut='valide')
    valider_candidatures.short_description = "Valider les candidatures sélectionnées"

    def rejeter_candidatures(self, request, queryset):
        queryset.update(statut='rejete')
    rejeter_candidatures.short_description = "Rejeter les candidatures sélectionnées"

    def colored_statut(self, obj):
        color = {
            'valide': 'green',
            'rejete': 'red',
            'en_traitement': 'orange',
            'envoye': 'blue',
            'non_envoye': 'gray',
            'traite': 'purple',
            'recours': 'brown',
        }.get(obj.statut, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_statut_display())
    colored_statut.short_description = "Statut"


@admin.register(Traitement)
class TraitementAdmin(admin.ModelAdmin):
    list_display = ('candidature', 'cv', 'lettre_de_motivation', 'piece_identite', 'aptitude_physique', 'titre_academique', 'observations', 'date_traitement', 'cv_link', 'lettre_motivation_link', 'piece_identite_link', 'aptitude_physique_link', 'titre_academique_link')
    list_filter = ('cv', 'lettre_de_motivation', 'piece_identite', 'aptitude_physique', 'titre_academique', 'date_traitement')
    search_fields = ('candidature__titre', 'observations')
    date_hierarchy = 'date_traitement'
    actions = ['marquer_traite']

    def marquer_traite(self, request, queryset):
        queryset.update(decision='traite')
    marquer_traite.short_description = "Marquer les traitements comme traités"

    def cv_link(self, obj):
        if obj.cv:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.cv.url)
        return "-"
    cv_link.short_description = "CV"

    def lettre_motivation_link(self, obj):
        if obj.lettre_motivation:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.lettre_motivation.url)
        return "-"
    lettre_motivation_link.short_description = "Lettre de motivation"

    def piece_identite_link(self, obj):
        if obj.piece_identite:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.piece_identite.url)
        return "-"
    piece_identite_link.short_description = "Pièce identité"

    def aptitude_physique_link(self, obj):
        if obj.aptitude_physique:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.aptitude_physique.url)
        return "-"
    aptitude_physique_link.short_description = "Aptitude physique"

    def titre_academique_link(self, obj):
        if obj.titre_academique:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.titre_academique.url)
        return "-"
    titre_academique_link.short_description = "Titre académique"


@admin.register(Recours)
class RecoursAdmin(admin.ModelAdmin):
    list_display = ('candidature', 'motif_rejet', 'traite', 'date_soumission')
    list_filter = ('traite', 'date_soumission')
    search_fields = ('candidature__titre', 'motif_rejet')
    actions = ['marquer_traite']

    def marquer_traite(self, request, queryset):
        queryset.update(traite=True)
    marquer_traite.short_description = "Marquer les recours comme traités"

    def candidature_link(self, obj):
        url = f"/admin/recrutement/candidature/{obj.candidature.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.candidature)
    candidature_link.short_description = "Candidature"


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_filter = ('created_at', 'title')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_filter = ('module',)
    search_fields = ('question',)


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    form = QuizAnswerAdminForm
    list_display = ('user', 'question', 'selected_option', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('user__username', 'question__question')
    date_hierarchy = 'answered_at'
    ordering = ('-answered_at',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_editable = ('is_read',)

# Register your models here.
