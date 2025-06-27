from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser

class Command(BaseCommand):
    help = "Create a new formateur user"

    def handle(self, *args, **kwargs):
        count = (CustomUser.objects.filter(role='formateur').count())+1
        email = f'formateur{count:03}@ena.cd'
        password = '123456#'

        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.create_user(email=email, password=password,username=email,is_active=True)
            user.role = 'formateur'
            user.date_de_naissance = '1975-01-01'
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User {email} created successfully!"))
        else:
            self.stdout.write(self.style.WARNING(f"User {email} already exists."))