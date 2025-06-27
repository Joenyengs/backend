from rest_framework.serializers import ModelSerializer, Serializer

from recrutement.models import Candidature
from .models import CustomUser, Notification, ProfilCandidat, RolePromotionRequest, SessionYear, UserRoles
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission, Group


class SessionYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionYear
        fields = ("id","debut_session", "fin_session", "promotion", "denomination",
                  "debut_soumission_candidature","fin_soumission_candidature","debut_soumission_recours",
                  "fin_soumission_recours", "is_current","can_submit_candidature")
        read_only_fields = ['id']


class CustomUserSerializer(ModelSerializer):
    has_applied = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    adresse_physique = serializers.SerializerMethodField()
    application_start_date = serializers.SerializerMethodField()
    can_submit_candidature = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "middle_name", "last_name", "username", "role", "is_active", 
                  "date_joined", "last_login", "telephone", "has_applied", "profile_picture", 
                  "adresse_physique", "application_start_date", "can_submit_candidature")
    
    def get_has_applied(self, obj):
        user = self.context['request'].user
        return Candidature.objects.filter(candidat=user).exists()
    
    def get_application_start_date(self, obj):
        u = self.context['request'].user
        user = CustomUser.objects.get(email=u)
        try:
            profil = ProfilCandidat.objects.get(user=user)
            session = SessionYear.objects.get(candidats=profil)
            return session.debut_soumission_candidature
        except Exception as e:
            print(e)
            return None
        
    def get_can_submit_candidature(self, obj):
        u = self.context['request'].user
        user = CustomUser.objects.get(email=u)
        try:
            profil = ProfilCandidat.objects.get(user=user)
            session = SessionYear.objects.get(candidats=profil)
            return session.can_submit_candidature
        except Exception as e:
            print(e)
            return None
    
    def get_profile_picture(self, obj):
        try:
            profil = ProfilCandidat.objects.get(user=obj)
            return profil.photo.url if profil.photo else None
        except ProfilCandidat.DoesNotExist:
            return None
    
    def get_adresse_physique(self, obj):
        try:
            profil = ProfilCandidat.objects.get(user=obj)
            return profil.adresse_physique if profil.adresse_physique else None
        except ProfilCandidat.DoesNotExist:
            return None


class ProfilCandidatSerializer(serializers.ModelSerializer):
    # photo_filename = serializers.ReadOnlyField()
    # photo_url = serializers.ReadOnlyField()
    class Meta:
        model = ProfilCandidat
        exclude = ['user']  # ou fields = '__all__' si tu veux tout exposer

        
class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = ['email','username','password','first_name','last_name']
        fields = ['first_name', "middle_name",'last_name', 'email','password', 'telephone']
        extra_kwargs = {"password":{"write_only":True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class LoginUserSerializer(Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Informations de connexion incorrectes!")
    

class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'role']
        extra_kwargs = {
            'role': {'required': True},
            'email': {'required': True}
        }


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    role = serializers.ChoiceField(choices=UserRoles.choices, required=True)


class ActivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password',]
        extra_kwargs = {
            'password': {'required': True},
        }

############################## Notifications ###############################
class NotificationSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        return [
            {
                "id": user.id,
                "email": user.email,
                "role": user.role
            }
            for user in obj.users.all()
        ]
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message','type', 'is_read', 'created_at', 'link', 'users']

############################################################################

class RolePromotionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePromotionRequest
        fields = ['requested_role', 'justification']


class CustomUserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    # has_applied = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'role', 'is_active', 'is_staff', 'permissions']
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    


    # def get_applications(self, obj):
    #     check = obj.candidatures
    #     cd = Candidature.objects.filter(id=check.id).count()
    #     print("counter:", cd)

    #     return cd

    def get_permissions(self, obj):
        a = obj.get_all_permissions()
        models_with_permissions = set()
        prefix = 'Gestion '
        for perm in a:
            try:
                app_label, codename = perm.split('.')
                model_name = codename.split('_', 1)[-1]
                models_with_permissions.add(f"{prefix}{model_name.capitalize()}")
            except Exception:
                continue
        return list(models_with_permissions)
    

class AllPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'content_type']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        # model = CustomUser.groups.through
        model = Group
        fields = ['id', 'name']
        read_only_fields = ['id']

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name
        }
    
        
