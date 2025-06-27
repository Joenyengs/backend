from django import forms
from .models import QuizAnswer, QuizQuestion

class QuizAnswerAdminForm(forms.ModelForm):
    class Meta:
        model = QuizAnswer
        fields = '__all__'

    class Media:
        js = ('js/quizanswer_dynamic.js',)  # On inclut notre JS custom

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Par défaut, on laisse les choix standards (A, B, C, D)