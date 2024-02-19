from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from Model.models import Utilisateur


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
