import pandas as pd
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .permissions import IsAdmin, IsCandidat, IsAlumni, IsTeacher, IsStudent
from rest_framework.generics import ListAPIView
from .models import CustomUser, Notification, ProfilAlumni, ProfilCandidat, ProfilEleve, ProfilFormateur, RolePromotionRequest, SessionYear, UserRoles
from .serializers import ActivateUserSerializer, AdminCreateUserSerializer, AllPermissionsSerializer, CustomUserListSerializer, CustomUserSerializer, FileUploadSerializer, GroupSerializer, NotificationSerializer, ProfilCandidatSerializer, RegisterUserSerializer, LoginUserSerializer, RolePromotionRequestSerializer, SessionYearSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.authentication import TokenAuthentication
from .authentication import CookieJWTAuthentication
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
from rest_framework_simplejwt.authentication import JWTAuthentication
from .tokens import account_activation_token
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
import random
import base64
from django.conf import settings
from django.core import signing
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.views import View
import os
from django.contrib.auth.models import Permission, Group
from rest_framework.decorators import action

FRONTEND_BASE_URL = os.environ.get("https://umojaapp.com", "http://localhost")  # Remplacez par votre URL frontend

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    """
    POST /forgot-password
    Body: { "email": "user@example.com" }
    """
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Aucun compte utilisateur enregistré avec cet email."}, status=status.HTTP_404_NOT_FOUND)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        # Utilisation de Django signing pour sécuriser le lien
        data = {"uid": uid, "token": token}
        encrypted_data = signing.dumps(data, salt="reset-password")
        reset_link = f"{FRONTEND_BASE_URL}/api/users/reset-password?data={encrypted_data}"
        send_mail(
            "Réinitialisation de mot de passe",
            f"Utilisez ce lien pour réinitialiser votre mot de passe : {reset_link}",
            "no-reply@ena.com",
            [email],
        )
        return Response({"message": "Email de réinitialisation envoyé."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    """
    POST /reset-password
    Body: { "password": "...", "data": "..."}
    """
    def post(self, request):
        encrypted_data = request.data.get("data")
        password = request.data.get("password")
        if not (encrypted_data and password):
            return Response({"error": "Données et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = signing.loads(encrypted_data, salt="reset-password", max_age=60*60*24)  # 24h expiration
            uidb64 = data.get("uid")
            token = data.get("token")
        except signing.BadSignature:
            return Response({"error": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        # Nettoyer l'OTP si nécessaire
        if hasattr(user, 'otp'):
            user.otp = None
        user.save()
        # Envoi d'une notification de succès
        notif = Notification.objects.create(
            message="Votre mot de passe a été réinitialisé avec succès.",
            link=f"{FRONTEND_BASE_URL}/login"
        )
        notif.users.set([self.request.user])
        return Response({"message": "Mot de passe réinitialisé."}, status=status.HTTP_200_OK)


class ExpiredLinkView(APIView):
    """
    GET /expired-link
    """
    def get(self, request):
        return Response({"error": "Lien expiré ou invalide."}, status=status.HTTP_400_BAD_REQUEST)


class OTPView(APIView):
    permission_classes = [AllowAny]
    """
    POST /otp
    Body: { "email": "...", "otp": "123456" }
    """
    otp_storage = {}  # À remplacer par Redis ou modèle en prod

    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).first()
        # password = request.data.get("password")
        otp = request.data.get("otp")
        if not email :  # or not password:
            return Response({"error": "Email requis."}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            # Générer et envoyer un OTP
            code = str(random.randint(100000, 999999))
            OTPView.otp_storage[email] = code
            user.otp = code  # Optionnel, si vous voulez stocker l'OTP dans le modèle utilisateur
            user.save()
            send_mail(
                "Votre code OTP",
                f"Votre code de vérification est : {code}",
                "no-reply@ena.com",
                [email],
            )
            return Response({"message": "OTP envoyé."}, status=status.HTTP_200_OK)
        
        # Vérifier l'OTP
        if user:
            if user.otp == otp:
                user.otp = None  # Nettoyer l'OTP après validation
                user.is_active = True
                user.save()

                # Retour de la réponse de succès
                return Response(
                    {
                        "success": True, 
                        #"token": access_token
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Si l'OTP est invalide, renvoie une erreur
                return Response({"error": "OTP invalide."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)


class UserInfoView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user
    

class CustomUserListView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserListSerializer
    permission_classes = [IsAdminUser]


class AdminUserListView(ListAPIView):
    # queryset = CustomUser.objects.filter(Q(is_staff=True) | Q(role='admin'))
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserListSerializer
    permission_classes = [IsAdminUser]


class AllPermissionsView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AllPermissionsSerializer
    queryset = Permission.objects.all()

    def get(self, request, *args, **kwargs):
        qrset = self.get_queryset()
        serializer = self.get_serializer(qrset, many=True)
        perms = serializer.data
        # Convertir les permissions en un format lisible
        readable_perms = []
        action_map = {
            'add': 'Création',
            'change': 'Modification',
            'delete': 'Suppression',
            'view': 'Consultation',
        }
        for perm in perms:
            try:
                action, model = perm['codename'].split('_', 1)
                action_label = action_map.get(action, action.capitalize())
                model_label = model.replace('_', ' ').capitalize()
                readable_perms.append(f"{action_label} {model_label}")
            except Exception:
                readable_perms.append(perm.codename)
        # Retourne la liste des permissions lisibles
        return Response({"permissions" : readable_perms}, status=status.HTTP_200_OK)


class SessionYearViewSet(viewsets.ModelViewSet):
    serializer_class = SessionYearSerializer
    permission_classes = [IsAdminUser | IsCandidat]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SessionYear.objects.all()
        # Return only the SessionYear associated with the current user's ProfilCandidat
        
        try:
            u = self.request.user
            user = CustomUser.objects.get(email=u)
            profil = ProfilCandidat.objects.get(user=user)

            if profil.session_id:
                session = SessionYear.objects.filter(id=profil.session_id).first()
                if session:
                    return SessionYear.objects.filter(id=session.id)
            else:
                return SessionYear.objects.none()
        except ProfilCandidat.DoesNotExist:
            return SessionYear.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    
class UserRegistrationView(CreateAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)  # Le compte n'est pas activé tant que l'OTP n'est pas validé
        
        # Générer un OTP et l'envoyer par email
        code = str(random.randint(100000, 999999))
        OTPView.otp_storage[user.email] = code
        user.otp = code  # Optionnel, si vous voulez stocker l'OTP dans le modèle utilisateur
        user.save()
        send_mail(
            "Votre code OTP",
            f"Votre code de vérification est : {code}",
            "no-reply@ena.com",
            [user.email],
        )

        # Envoi d'une notification de bienvenue
        if user.role == 'candidat':
            profil = ProfilCandidat.objects.create(user=user)
            profil.save()
            # Envoi d'une notification de bienvenue
            notif = Notification.objects.create(
                message="Bienvenue ! Merci de compléter votre profil candidat pour pouvoir soumettre une candidature.",
                link=f"{FRONTEND_BASE_URL}/profil"
            )
            notif.users.set([user])
            
        ### Les autres profils seront créés automatiquement lors de l'approbation de la requete 
        # de promotion du role par l'administrateur

        # elif user.role == 'alumni':
        #     profil = ProfilAlumni.objects.create(user=user)
        #     profil.save()

        # elif user.role == 'formateur':
        #     profil = ProfilFormateur.objects.create(user=user)
        #     profil.save()

        # elif user.role == 'eleve':
        #     profil = ProfilEleve.objects.create(user=user)
        #     profil.save()

        # elif user.role == 'evaluateur':
        #     profil = ProfilEvaluateur.objects.create(user=user)
        #     profil.save()
    

class ProfilCandidatUpdateView(RetrieveUpdateAPIView):
    serializer_class = ProfilCandidatSerializer
    permission_classes = [IsCandidat]
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        # On suppose que le profil est lié à l'utilisateur connecté
        # profil, created = ProfilCandidat.objects.get_or_create(user=self.request.user)
        profil = ProfilCandidat.objects.get(user=self.request.user)
        return profil
    
    def perform_update(self, serializer):
        profil = serializer.save()
        # Si une photo est fournie, on la sauvegarde
        if 'photo' in self.request.FILES:
            profil.photo = self.request.FILES['photo']
            profil.save()
        # Envoi d'une notification de mise à jour du profil
        notif = Notification.objects.create(
            message="Votre profil candidat a été mis à jour avec succès.",
            link=f"{FRONTEND_BASE_URL}/profil"
        )
        notif.users.set([self.request.user])

    def partial_update(self, request, *args, **kwargs):
        # On permet la mise à jour partielle du profil
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        return super().partial_update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        # On permet la mise à jour partielle du profil
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        return super().patch(request, *args, **kwargs)
    
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = (JWTAuthentication,)

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)

        #generate tokens
        if serializer.is_valid():
            user = serializer.validated_data
            user.last_login = datetime.now()
            user.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                # "user": CustomUserSerializer(user).data['username']
                "access_token":str(access_token),
                "refresh_token":str(refresh),
                "userId":user.id,
                },
                status=status.HTTP_200_OK)
            
            response.set_cookie(key="access_token", 
                                value=access_token,
                                httponly=True,
                                secure=True,
                                samesite="None")
            
            response.set_cookie(key="refresh_token", 
                                value=refresh,
                                httponly=True,
                                secure=True,
                                samesite="None")
            
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

User = get_user_model()

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Specify your Google client ID here
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), "104917716492-ip00rcnu4rggumgulhtbtmhqjfjtcgbi.apps.googleusercontent.com")
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            # Get or create user
            user, created = User.objects.get_or_create(email=email, defaults={
                'username': email.split('@')[0],
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            })
            # Optionally update names if changed
            if not created:
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception as e:
                return Response({"erreur":"Erreur jeton invalide:" + str(e) }, status=status.HTTP_400_BAD_REQUEST)
        
        response = Response({"message": "Déconnecté avec succès!"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"erreur":"Jeton d'actualisation non fourni"}, status= status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({"message":"Jeton d'accès actualisé avec succès"}, status=status.HTTP_200_OK)
            response.set_cookie(key="access_token", 
                                value=access_token,
                                httponly=True,
                                secure=True,
                                samesite="None")

            return response
        except InvalidToken:
            return Response({"erreur":"Jeton invalide"}, status=status.HTTP_401_UNAUTHORIZED)

################################### Notifications ###############################
class UserNotificationsView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    #authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.all().order_by('-created_at')
        return Notification.objects.filter(users=user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """ Overriding the list method to include additional data for superusers."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if request.user.is_superuser:
            compteurs = Notification.objects.count()
            notifications_non_lues = Notification.objects.filter(is_read=False).count()
            return Response({
                "compteur": compteurs,
                "notifications_non_lues": notifications_non_lues,
                "liste_notifications": serializer.data
            })
        return Response(serializer.data)
    
    def notifications_groupe_by_user():
        from collections import defaultdict
        notifications = Notification.objects.all().order_by('-created_at')
        grouped = defaultdict(list)
        for notif in notifications:
            grouped[notif.user_id].append(notif)
        
        return grouped
        # grouped is now a dict: {user_id: [notif1, notif2, ...]}


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Permet :
        (1) à l'utilisateur concerné de lire des notifications relatives à son compte;
        (2) à l'administrateur de consulter et de générer des notifications.
    """
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.all().order_by('-created_at')
        return Notification.objects.filter(users=user).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """ Overriding the list method to include additional data for superusers."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if request.user.is_superuser:
            compteurs = Notification.objects.count()
            notifications_non_lues = Notification.objects.filter(is_read=False).count()
            return Response({
                "compteur": compteurs,
                "notifications_non_lues": notifications_non_lues,
                "liste_notifications": serializer.data
            })
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def grouped():
        from collections import defaultdict
        notifications = Notification.objects.all().order_by('-created_at')
        grouped = defaultdict(list)
        for notif in notifications:
            grouped[notif.user_id].append(notif)
        
        return grouped


# PATCH /notifications/<int:pk>/read/
class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return Response({"success": True})
    
################################## ADMIN ###############################
class UserListView(ListAPIView):
    serializer_class = CustomUserListSerializer
    permission_classes = [IsAdminUser | IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class UserDetailView(RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser, IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.all()
    

def extract_username_from_email(email):
    """Extracts the username from the email address."""
    return email.split('@')[0] if '@' in email else email

    
class AdminCreateUserView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminCreateUserSerializer

    def post(self, request):
        serializer = AdminCreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        role = serializer.validated_data['role']
        # if role == "candidat":
        #     return Response({"erreur": "Utilisez l'inscription classique pour les candidats."}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(email=email).exists():
            return Response({"erreur": "Utilisateur déjà existant."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.create(email=email, role=role, is_active=False)
        user.username = extract_username_from_email(email)
        user.set_unusable_password()  # Empêche la connexion tant que le mot de passe n'est pas défini
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        # activation_path = reverse('activate-user', kwargs={'uidb64': uid, 'token': token})
        activation_path = reverse('activate-user', kwargs={'uidb64': uid, 'token': token})
        activation_link = f"{FRONTEND_BASE_URL}{activation_path}"
        msg = f"Votre compte a été créé. Prière de l'activer à travers ce lien : "
        # Envoi d'une notification de bienvenue
        # On suppose que l'activation du compte se fait par un lien envoyé par email
        # On crée une notification pour l'utilisateur
        Notification.objects.create(
            users=user,
            message=msg,
            link=f"{activation_link}"
        )
        # print(f"Activation mail to {email}: {activation_link}")
        send_mail(
            "Activation de votre compte",
            f"{msg} : {activation_link}",
            "no-reply@ena.com",
            [email],
        )
        return Response({"message": "Utilisateur créé, email d'activation envoyé."}, status=status.HTTP_201_CREATED)
    

class AdminBulkCreateUserView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser]
    serializer_class = FileUploadSerializer

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        file_obj = None
        role = ""
        if serializer.is_valid():
            file_obj = serializer.validated_data['file']
            role = serializer.validated_data['role']
        if not file_obj or not role:
            return Response({"erreur": "Fichier et rôle requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = pd.read_excel(file_obj, engine='openpyxl')
        except Exception as e:
            return Response({"erreur": f"Erreur de lecture du fichier : {e}"}, status=status.HTTP_400_BAD_REQUEST)
        if 'email' not in df.columns:
            return Response({"erreur": "La colonne 'email' est requise dans le fichier."}, status=status.HTTP_400_BAD_REQUEST)
        created, exists = [], []
        for email in df['email'].dropna().unique():
            if CustomUser.objects.filter(email=email).exists():
                exists.append(email)
                continue
            user = CustomUser.objects.create(email=email, role=role, is_active=False)
            user.username = extract_username_from_email(email)
            user.set_unusable_password()
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            # Chiffrer les données sensibles (uid et token) avant de les inclure dans le lien
            data = {"uid": uid, "token": token}
            encrypted_data = signing.dumps(data, salt="activate-user")
            activation_link = f"{FRONTEND_BASE_URL}/activer?data={encrypted_data}"

            # Envoi d'une notification de bienvenue
            msg = f"Votre compte a été créé. Prière de l'activer à travers ce lien : "
            notif = Notification.objects.create(
                message=msg,
                link=f"{activation_link}"
            )
            notif.users.set([self.request.user])
            send_mail(
                "Activation de votre compte",
                f"{msg} : {activation_link}",
                "no-reply@ena.com",
                [email],
            )
            created.append(email)
        return Response({
            "comptes_crees": created,
            "comptes_existants": exists
        }, status=status.HTTP_201_CREATED)


class ActivateUserByLinkView(APIView):
    serializer_class = ActivateUserSerializer
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user and account_activation_token.check_token(user, token):
            return Response({"uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
        return Response({"erreur": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token):
        password = request.data.get("password")
        if not password:
            return Response({"erreur": "Mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"erreur": "Utilisateur introuvable."}, status=status.HTTP_400_BAD_REQUEST)
        # Vérifie le token d'activation
        try:
            activatation_notification = Notification.objects.filter(users=user, link__contains=token).first()
            activatation_notification.is_read = True
            activatation_notification.save()
        except Notification.DoesNotExist:
            return Response({"erreur": "Notification d'activation introuvable."}, status=status.HTTP_400_BAD_REQUEST)
        
        if account_activation_token.check_token(user, token):
            user.set_password(password)
            user.is_active = True
            user.save()
            return Response({"message": "Mot de passe défini, compte activé."}, status=status.HTTP_200_OK)
        # Si le token n'est pas valide, renvoie une erreur
        return Response({"erreur": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
    

class StaffUserListView(ListAPIView):
        serializer_class = CustomUserSerializer
        permission_classes = [IsAdminUser]
        
        def get_queryset(self):
            return CustomUser.objects.filter(is_staff=True)
        

class GetProfilCandidatByEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email):
        try:
            user = CustomUser.objects.get(email=email)
            if user == request.user or request.user.role == 'candidat':
                profil = ProfilCandidat.objects.get(user=user)
            else:
                return Response({"error": "Vous n'êtes pas autorisé à accéder au profil de cet utilisateur."}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except ProfilCandidat.DoesNotExist:
            return Response({"error": "Profil candidat introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfilCandidatSerializer(profil)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfilCandidatUpdateView(RetrieveUpdateAPIView):
    serializer_class = ProfilCandidatSerializer
    permission_classes = [IsCandidat]
    # authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return ProfilCandidat.objects.get(user=self.request.user)
            
    def perform_update(self, serializer):
        profil = serializer.save()
        # Si une photo est fournie, on la sauvegarde
        if 'photo' in self.request.FILES:
            profil.photo = self.request.FILES['photo']
            profil.save()

        # Envoi d'une notification de mise à jour du profil
        notif = Notification.objects.create(
            message="Votre profil candidat a été mis à jour avec succès.",
            link="/profil"
        )
        notif.users.set([self.request.user])

    def partial_update(self, request, *args, **kwargs):
        # On permet la mise à jour partielle du profil
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # Envoi d'une notification de mise à jour du profil
        notif = Notification.objects.create(
            message="Votre profil candidat a été partiellement mis à jour avec succès.",
            link="/profil"
        )
        notif.users.set([self.request.user])
        # Retourne la réponse de mise à jour partielle
        return super().partial_update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return super().patch(request, *args, **kwargs)

    
class UserRolesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Suppose que les rôles sont définis dans le modèle CustomUser sous forme de choix
        roles = [{"value": choice[0], "label": choice[1]} for choice in UserRoles.choices]
        return Response({"roles": roles}, status=status.HTTP_200_OK)
    

class DomaineEtudeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Les domaines sont définis dans le modèle ProfilCandidat sous forme de choix
        domaines = [{"value": choice[0], "label": choice[1]} for choice in ProfilCandidat.DOMAINES_ETUDE]
        return Response({"domaines": domaines}, status=status.HTTP_200_OK)


class RolePromotionRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RolePromotionRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifier si une demande de promotion en attente existe déjà pour cet utilisateur
            if RolePromotionRequest.objects.filter(user=request.user, status='pending').exists():
                return Response({"error": "Vous avez déjà une demande de promotion en attente."}, status=status.HTTP_403_FORBIDDEN)
            
            request =  RolePromotionRequest.objects.create(
                user=request.user,
                requested_role=serializer.validated_data['requested_role'],
                justification=serializer.validated_data.get('justification', '')
            )
            # Envoi d'une notification :
            # 1. à l'auteur de la requête
            # 2. aux administrateurs
            # On suppose que les administrateurs sont ceux qui ont le rôle 'admin' ou sont superutilisateurs
            destinataires = CustomUser.objects.filter(
                (Q(role='admin') | Q(is_superuser=True)) & Q(is_active=True)
            ).union(CustomUser.objects.filter(pk=request.user.pk))

            notif = Notification.objects.create(
                message="Votre demande de promotion a été envoyée avec succès.",
                link="/profil"
            )
            notif.users.set([destinataires])
            return Response({"detail": "Demande de promotion envoyée."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersWithPromotionRequestsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.filter(
            promotion_requests__status='pending'
        ).distinct().prefetch_related(
            Prefetch(
                'promotion_requests',
                queryset=RolePromotionRequest.objects.filter(status='pending').order_by('-created_at')
            )
        )

        data = []
        for user in users:
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "promotion_requests": [
                    {
                        "id": str(req.id),
                        "requested_role": req.requested_role,
                        "justification": req.justification,
                        "status": req.status,
                        "created_at": req.created_at,
                        "reviewed_at": req.reviewed_at,
                        "reviewed_by": req.reviewed_by.email if req.reviewed_by else None,
                        "admin_comment": req.admin_comment,
                    }
                    for req in user.promotion_requests.all()
                ]
            }
            data.append(user_data)
        # Retourne les données sous forme de JSON
        return Response(data, status=status.HTTP_200_OK)


class ReplyRolePromotionRequestView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            pk = request.data.get("user_id")
            db_user = CustomUser.objects.get(id=pk)
            # Vérifier si l'utilisateur a une demande de promotion en attente
            if not RolePromotionRequest.objects.filter(user=db_user, status='pending').exists():
                return Response({"error": "Aucune demande de promotion en attente pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
            role_request = RolePromotionRequest.objects.get(user=db_user, status='pending')
        except RolePromotionRequest.DoesNotExist:
            return Response({"error": "Requête de promotion introuvable ou déjà traitée."}, status=status.HTTP_404_NOT_FOUND)
        
        decision_choice = request.data.get("decision", "")
        admin_comment = request.data.get("comment", "")

        if decision_choice not in ["approved", "rejected"]:
            return Response({"error": "Statut invalide. Utilisez 'approved' ou 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        
        role_request.status = decision_choice
        role_request.reviewed_by = request.user
        role_request.admin_comment = admin_comment
        role_request.reviewed_at = datetime.now()
        role_request.save()

        # Si approuvé, changer le rôle de l'utilisateur
        if decision_choice == "approved":
            db_user = role_request.user
            db_user.role = role_request.requested_role
            db_user.save()
            notif_msg = f"Votre demande de promotion au rôle '{role_request.requested_role}' a été approuvée."
        else:
            notif_msg = f"Votre demande de promotion au rôle '{role_request.requested_role}' a été rejetée.\nCommentaires : {admin_comment}"
        
        notif = Notification.objects.create(
            message=notif_msg,
            link="/profil"
        )
        notif.users.set([role_request.user])

        return Response({"message": "Requête traitée."}, status=status.HTTP_200_OK)
    

class ActiveGroupsListView(ListAPIView):
    queryset = Group.objects.filter(user__is_active=True).distinct()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
    
