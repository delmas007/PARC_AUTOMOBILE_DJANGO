from utilisateurs.views import Accueil_user, inscription_user, Connexion_user, Compte, vehicule_details, list_vehicule, \
    Acceuil_conducteur, activate, password_reset_request
from django.urls import path

app_name = 'utilisateur'

urlpatterns = [
    path('Accueil', Accueil_user, name='Accueil_user'),
    path('Vehicule', list_vehicule, name='list_vehicule'),
    path('Compte', Compte, name='compte'),
    path('Inscription/', inscription_user, name='Inscription_user'),
    path('Connexion/', Connexion_user.as_view(), name='connexion_user'),
    path('Vehicule/<int:vehicule_id>/', vehicule_details, name='Vehicule_details'),
    path('Acceuil_conducteur', Acceuil_conducteur, name='Acceuil_conducteur'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path("password_reset", password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', passwordResetConfirm, name='réinitialisation'),
]
