from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from Model.models import Utilisateur
from django import forms


class ConnexionForm(AuthenticationForm):
    class Meta:
        model = Utilisateur
        fields = 'username', 'password'


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = 'username', 'email', 'nom', 'prenom', 'conducteur'


class UserRegistrationForme(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = 'username', 'email', 'nom', 'prenom', 'conducteur', 'roles'


class UserRegistrationFormee(UserChangeForm):
    class Meta:
        model = Utilisateur
        fields = 'email', 'nom', 'prenom'
