from django.urls import path, include
from .views import ActivateUserByLinkView, ActiveGroupsListView, AdminBulkCreateUserView, AdminCreateUserView, AdminUserListView, AllPermissionsView, CustomUserListView, DomaineEtudeView, GetProfilCandidatByEmailView, MarkNotificationReadView, NotificationViewSet, ProfilCandidatUpdateView, ReplyRolePromotionRequestView, RolePromotionRequestAPIView, SessionYearViewSet, StaffUserListView, UserInfoView, UserListView, UserNotificationsView, UserRegistrationView, LoginView, LogoutView, CookieTokenRefreshView, GoogleLoginView, ForgotPasswordView, ExpiredLinkView, ResetPasswordView, OTPView, UserRolesView, UsersWithPromotionRequestsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'session-year', SessionYearViewSet, basename='session-year')

urlpatterns = [
    path("", include(router.urls)),
    ################################ AUTH ###############################
    path("user-info/", UserInfoView.as_view(), name="user-info"),
    path("user-list/", UserListView.as_view(), name="user-list"),
    path("custom-user-list/", CustomUserListView.as_view(), name="custom-user-list"),
    
    # liste des administrateurs
    path("admin-user-list/", AdminUserListView.as_view(), name="admin-user-list"),
    path("active-groups-list/", ActiveGroupsListView.as_view(), name="active-groups-list"),
    
    path("permissions/", AllPermissionsView.as_view(), name="permissions"),
    path("register/", UserRegistrationView.as_view(), name="register-user"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path('activate/<uidb64>/<token>/', ActivateUserByLinkView.as_view(), name='activate-user'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('expired-link/', ExpiredLinkView.as_view(), name='expired-link'),
    path('otp/', OTPView.as_view(), name='otp'),
    path('profil-candidat/', ProfilCandidatUpdateView.as_view(), name='profil-candidat'),
    path('staff-users-list/', StaffUserListView.as_view(), name='staff-users-list'),
    path('user-roles-view/', UserRolesView.as_view(), name='user-roles-view'),
    path('domaines-etude-view/', DomaineEtudeView.as_view(), name='domaines-etude-view'),
    path('role-promotion-request/', RolePromotionRequestAPIView.as_view(), name='role-promotion-request'),
    # path('role-promotion-reply/', RolePromotionReplyAPIView.as_view(), name='role-promotion-reply'),
    path('users-promotion-requests/', UsersWithPromotionRequestsView.as_view(), name='users-promotion-requests'),
    path('profile-by-email/', GetProfilCandidatByEmailView.as_view(), name='profile-by-email'),
    path('process-role-promotion-request/', ReplyRolePromotionRequestView.as_view(), name='process-role-promotion-request'),

    ############################ NOTIFICATIONS ###########################
    # path("notifications/", UserNotificationsView.as_view(), name="user-notifications"),
    # path("notifications/", NotificationViewSet.as_view({'get': 'list'}), name="user-notifications"),
    # path("notifications/", NotificationViewSet.as_view(), name="user-notifications"),
    path("notifications/<uuid:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),

    ############################## ADMIN ###############################
    path('admin-create-user/', AdminCreateUserView.as_view(), name='admin-create-user'),
    path('admin-bulk-create/', AdminBulkCreateUserView.as_view(), name='admin-bulk-create'),
    
]
