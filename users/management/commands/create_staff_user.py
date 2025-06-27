from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser

class Command(BaseCommand):
    help = "Create a new admin user"

    def handle(self, *args, **kwargs):
        count = (CustomUser.objects.filter(role='admin').count())+1
        email = f'admin{count:03}@ena.cd'
        password = '123456#'

        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.create_user(email=email, password=password, username=email)
            user.is_staff = True
            user.role = 'admin'  # Assuming you have a role field in your CustomUser model
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Staff User {email} created successfully!"))
        else:
            self.stdout.write(self.style.WARNING(f"Staff User {email} already exists."))