from utilisateurs.views import Accueil_user
from django.urls import path

urlpatterns = [
    path('Accueil', Accueil_user, name='Accueil_user'),
]
