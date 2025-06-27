from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Import local pour éviter AppRegistryNotReady
        from django.contrib.auth.models import Group

        groups = ["Candidat", "Administrateur", "Recruteur"]

        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
