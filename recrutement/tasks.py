from celery import shared_task
from .models import Candidature
from django.db.models import F

def process_candidature(candidature, evaluateur):
    """
    Traite une candidature selon le rôle de l'évaluateur.
    Args:
        candidature (Candidature): La candidature à traiter.
        evaluateur (User): L'utilisateur évaluateur qui traite.
    """
    if getattr(evaluateur, 'role', None) == 'evaluateur1':
        candidature.statut = 'en_traitement'
    elif getattr(evaluateur, 'role', None) == 'evaluateur2':
        candidature.statut = 'traitee'
    candidature.traite_par = evaluateur
    candidature.save()

@shared_task
def traiter_lot_candidatures(candidature_ids, evaluateur_email):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        evaluateur = User.objects.get(email=evaluateur_email)
    except User.DoesNotExist:
        return  # ou log une erreur

    for cid in candidature_ids:
        try:
            candidature = Candidature.objects.get(id=cid)
            process_candidature(candidature, evaluateur)
        except Candidature.DoesNotExist:
            continue