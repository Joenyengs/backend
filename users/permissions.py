from rest_framework.permissions import BasePermission


class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.is_staff or obj.candidature.candidat == request.user)

class IsAdmin(BasePermission):
    """Accès uniquement aux admins."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.role == "admin") or request.user.is_superuser


class IsAlumni(BasePermission):
    """Accès uniquement aux alumni."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "alumni"
    

class IsTeacher(BasePermission):
    """Accès uniquement aux formateurs."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "formateur"
    

class IsStudent(BasePermission):
    """Accès uniquement aux élèves."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "eleve"
    

class IsCandidat(BasePermission):
    """Accès uniquement aux candidats (futurs élèves)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "candidat"
    

class IsStaff(BasePermission):
    """Accès uniquement au personnel administratif."""
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.role == "admin"