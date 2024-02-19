from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from Model.forms import ConnexionForm, UserRegistrationForm
from Model.models import Roles


# Create your views here.

class Connexion(LoginView):
    template_name = 'connexion.html'
    form_class = ConnexionForm

    def get_success_url(self) -> str:
        if self.request.user.roles.role == 'ADMIN':
            return reverse('admins:Ajout_gestionnaire')
        elif self.request.user.roles.role == 'GESTIONNAIRE':
            return reverse('Accueil')


class Deconnexion(LogoutView):
    pass



