from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from Model.models import Utilisateur
from django import forms


class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(ConnexionForm, self).__init__(*args, **kwargs)

        self.fields['username'].error_messages = {
            'required': "Veuillez saisir un Nom d'utilisateur valide !!"
        }
        self.fields['password'].error_messages = {
            'required': "Veuillez saisir un mot de passe valide !!"
        }
        # self.error_messages = {
        #     "invalid_login":
        #         "Veuillez saisir les mêmes informations que lors de la création de votre compte. "
        #         "Vous devez respecter les majuscules ou les minuscules !!",
        #     "inactive": "Ce compte est inactif veuillez contacter votre administrateur."
        # }

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
