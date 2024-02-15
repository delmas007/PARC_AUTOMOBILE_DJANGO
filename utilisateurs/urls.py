from utilisateurs.views import Accueil_user, inscription_user
from django.urls import path

app_name = 'utilisateur'

urlpatterns = [
    path('Accueil', Accueil_user, name='Accueil_user'),
    path('Inscription/', inscription_user, name='Inscription_user'),
]
