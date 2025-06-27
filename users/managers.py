from django.contrib.auth.models import BaseUserManager, GroupManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email requis.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("username", "Administrator")
        

        if not extra_fields.get("is_staff"):
            raise ValueError("Le superutilisateur doit avoir is_staff à True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Le superutilisateur doit avoir is_superuser à True")
        if not extra_fields.get("role")== "admin":
             # Vérifie si le rôle est défini sur "admin"
            raise ValueError("Le superutilisateur doit avoir un rôle admin")
        return self.create_user(email, password, **extra_fields)
    
class CustomGroupManager(GroupManager):
    def create_group(self, name, **extra_fields):
        if not name:
            raise ValueError("Le nom du groupe est requis.")
        group = self.model(name=name, **extra_fields)
        group.save()
        return group
    
    def get_or_create_group(self, name, **extra_fields):
        group, created = self.get_or_create(name=name, defaults=extra_fields)
        return group, created