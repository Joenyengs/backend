from django.contrib import admin
from .models import CustomUser, ProfilCandidat, SessionYear

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass

@admin.register(ProfilCandidat)
class ProfilCandidatAdmin(admin.ModelAdmin):
    pass

@admin.register(SessionYear)
class SessionYearAdmin(admin.ModelAdmin):
    list_display = ('debut_session','fin_session','promotion','denomination')    #is_current
    list_filter = ('debut_session','fin_session')
    search_fields = ('promotion','denomination')
# Register your models here.
