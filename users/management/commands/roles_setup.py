from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from recrutement.models import Candidature, Recours 
from users.models import ProfilAlumni, ProfilCandidat, ProfilEleve, ProfilFormateur 
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Create user groups and assign permissions"
    
    def handle(self, *args, **kwargs):
        # Créer les groupes
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        eval_group, _ = Group.objects.get_or_create(name="Evaluateur")
        candidat_group, _ = Group.objects.get_or_create(name="Candidat")
        alumni_group, _ = Group.objects.get_or_create(name="Alumni")
        formateur_group, _ = Group.objects.get_or_create(name="Formateur")
        eleve_group, _ = Group.objects.get_or_create(name="Eleve")

        # Donne tous les droits aux admins
        admin_group.permissions.set(Permission.objects.all())

        # Limite les droits des évaluateurs
        content_types_eval = ContentType.objects.get_for_models(Candidature, Recours)
        permissions_eval = Permission.objects.filter(content_type__in=content_types_eval.values())
        eval_group.permissions.set(permissions_eval)

        # Limite les droits des candidats
        content_types_candidats = ContentType.objects.get_for_models(ProfilCandidat, Candidature, Recours)
        permissions_candidats = Permission.objects.filter(content_type__in=content_types_candidats.values())
        candidat_group.permissions.set(permissions_candidats)

        # Limite les droits des alumni
        content_types_alumni = ContentType.objects.get_for_models(ProfilAlumni)
        permissions_alumni = Permission.objects.filter(content_type__in=content_types_alumni.values())
        alumni_group.permissions.set(permissions_alumni)

        # Limite les droits des formateurs
        content_types_formateurs = ContentType.objects.get_for_models(ProfilFormateur)
        permissions_formateurs = Permission.objects.filter(content_type__in=content_types_formateurs.values())
        formateur_group.permissions.set(permissions_formateurs)

        # Limite les droits des élèves
        content_types_eleves = ContentType.objects.get_for_models(ProfilEleve)
        permissions_eleves = Permission.objects.filter(content_type__in=content_types_eleves.values())
        eleve_group.permissions.set(permissions_eleves)

        # Enregistre les groupes
        admin_group.save()
        eval_group.save()
        candidat_group.save()
        alumni_group.save()
        formateur_group.save()
        eleve_group.save()

