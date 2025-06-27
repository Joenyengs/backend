from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CandidatureCreateView, CandidatureStatusView, ExportCandidatureTraiteesParPremierEvaluateurExcelView, ExportCandidatureTraiteesParSecondEvaluateurExcelView, ExportCandidatureTraiteesParTroisiemeEvaluateurExcelView, ListeCandidaturesView, RecoursStatusView, RecoursViewSet, StatsCandidaturesNonTraiteesView, 
                    StatsCandidaturesParProvinceParGenreView, StatsCandidaturesTraiteesParPremierEvaluateurView, 
                    StatsCandidaturesTraiteesParSecondEvaluateurView, CandidaturesATraiterView, 
                    CandidaturesRetenuesStatsView, ExportCandidatureStatsExcelView, 
                    ExportCandidaturesNonRetenuesExcelView, ExportCandidaturesRetenuesExcelView, 
                    HistoriqueTraitementsView, RecoursHistoryView, StatsCandidaturesTraiteesParTroisiemeEvaluateurView, TrainingModulesProgressView, 
                    CandidateQuizAnswersView, CandidateStartedModulesView, CandidatureViewSet, 
                    SubmitQuizAnswerView, TrainingModuleListView, TrainingModuleDetailView, TraiterCandidatureView, 
                    TraiterRecoursView, get_question_options, EvaluerCandidatureView)

router = DefaultRouter()
router.register(r'candidatures', CandidatureViewSet, basename='candidatures')
router.register(r'recours', RecoursViewSet, basename='recours')

urlpatterns = [
    path("", include(router.urls)),

    path("candidatures-add/", CandidatureCreateView.as_view(), name="candidature-ajout"),
    path("candidatures-get/", ListeCandidaturesView.as_view(), name="liste-candidatures"),
    # path("candidature/<uuid:pk>/", CandidatureViewSet.as_view(), name="candidature-detail"),
    # Statut du dossier du candidat
    path('candidature/statut/', CandidatureStatusView.as_view(), name='candidature-statut'),
    path('recours/statut/', RecoursStatusView.as_view(), name='recours-statut'),
    # path("recours/", RecoursListView.as_view(), name="liste-recours"),
    # path("recours/add/", AjoutRecoursView.as_view(), name="recours-ajout"),

    #TRAINING MODULES
    path("training/", TrainingModuleListView.as_view(), name="training-list"),
    path("training/<uuid:pk>/", TrainingModuleDetailView.as_view(), name="training-detail"),
    path('training/quiz-submit/', SubmitQuizAnswerView.as_view(), name='training-quiz-submit'),
    path('training/quiz-answers/', CandidateQuizAnswersView.as_view(), name='training-quiz-answers'),
    path('training/progress/', TrainingModulesProgressView.as_view(), name='training-modules-progress'),
    path('training/started-modules/', CandidateStartedModulesView.as_view(), name='training-started-modules'),
    path('admin/get-question-options/<uuid:question_id>/', get_question_options, name='get_question_options'),

    # ADMINISTRATION
    path("candidature/<uuid:pk>/traiter/", TraiterCandidatureView.as_view(), name="traiter-candidature"),
    path("candidatures/a-traiter/", CandidaturesATraiterView.as_view(), name="candidatures-a-traiter"),
    path('stats-province-genre/', StatsCandidaturesParProvinceParGenreView.as_view(), name='stats-province-genre'),
    path('stats-premier-evaluateur/', StatsCandidaturesTraiteesParPremierEvaluateurView.as_view(), name='candidature-stats-premier-evaluateur'),
    path('stats-second-evaluateur/', StatsCandidaturesTraiteesParSecondEvaluateurView.as_view(), name='candidature-stats-second-evaluateur'),
    path('stats-troisieme-evaluateur/', StatsCandidaturesTraiteesParTroisiemeEvaluateurView.as_view(), name='candidature-stats-troisieme-evaluateur'),
    path('stats-non-traitees/', StatsCandidaturesNonTraiteesView.as_view(), name='candidature-stats-non-traitees'),
    path('stats-retenues/', CandidaturesRetenuesStatsView.as_view(), name='candidature-stats-retenues'),
    path('stats-export-retenues-excel/', ExportCandidaturesRetenuesExcelView.as_view(), name='export-candidatures-retenues-excel'),
    path('stats-export-stats-excel/', ExportCandidatureStatsExcelView.as_view(), name='export-candidature-stats-excel'),
    path(
        'export-stats-premier-evaluateur-excel/',
        ExportCandidatureTraiteesParPremierEvaluateurExcelView.as_view(),
        name='export-stats-premier-evaluateur-excel'
    ),
    path(
        'export-stats-second-evaluateur-excel/',
        ExportCandidatureTraiteesParSecondEvaluateurExcelView.as_view(),
        name='export-stats-second-evaluateur-excel'
    ),
    path(
        'export-stats-troisieme-evaluateur-excel/',
        ExportCandidatureTraiteesParTroisiemeEvaluateurExcelView.as_view(),
        name='export-stats-troisieme-evaluateur-excel'
    ),
    path(
        'export-stats-non-retenues-excel/',
        ExportCandidaturesNonRetenuesExcelView.as_view(),
        name='export-candidatures-non-retenues-excel'
    ),
    path('historique-traitements-candidatures/', HistoriqueTraitementsView.as_view(), name='historique-traitements-candidature'),
    path('evaluer-candidature/', EvaluerCandidatureView.as_view(), name='evaluer-candidature'),
    
    
    path("recours/<uuid:pk>/traiter/", TraiterRecoursView.as_view(), name="traiter-recours"),
    path("recours/<uuid:pk>/historique/", RecoursHistoryView.as_view(), name="recours-historique"),
    
]
