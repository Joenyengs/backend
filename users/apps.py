from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        try:
            from django.contrib.auth.models import Group

            groups = ["Candidat", "Administrateur", "Recruteur"]

            for group_name in groups:
                Group.objects.get_or_create(name=group_name)

        except (OperationalError, ProgrammingError):
            # On ignore l'erreur en l'absence des tables
            pass
