from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser

class Command(BaseCommand):
    help = "Create a new candidat user"

    def handle(self, *args, **kwargs):
        count = (CustomUser.objects.filter(role='candidat').count())+1
        email = f'candidat{count:03}@ena.cd'
        password = '123456#'

        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.create_user(email=email, password=password,username=email,is_active=True)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User {email} created successfully!"))
        else:
            self.stdout.write(self.style.WARNING(f"User {email} already exists."))