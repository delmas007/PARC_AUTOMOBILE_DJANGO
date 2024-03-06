from django.urls import path

from entretien.views import Ajouter_Entretien

app_name = 'entretien'

urlpatterns = [
    path('Ajouter_Entretien/', Ajouter_Entretien, name='Ajouter_Entretien'),
]