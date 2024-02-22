from utilisateurs.views import Accueil_user, inscription_user, Connexion_user, Compte, vehicule_details, list_vehicule
from django.urls import path

app_name = 'utilisateur'

urlpatterns = [
    path('Accueil', Accueil_user, name='Accueil_user'),
    path('Vheicule', list_vehicule, name='list_vehicule'),
    path('Compte', Compte, name='compte'),
    path('Inscription/', inscription_user, name='Inscription_user'),
    path('Connexion/', Connexion_user.as_view(), name='connexion_user'),
    path('Vehicule/<int:vehicule_id>/', vehicule_details, name='Vehicule_details'),
]
