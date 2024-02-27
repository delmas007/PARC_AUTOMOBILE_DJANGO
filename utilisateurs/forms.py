from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from Model.models import Conducteur, Utilisateur, Demande_prolongement
from django import forms


# Create your models here.

class ConducteurClientForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = '__all__'


class PasswordResetForme(PasswordResetForm):
    class Meta:
        model = Utilisateur
        fields = 'email'


class ChangerMotDePasse(SetPasswordForm):
    class Meta:
        model = Utilisateur
        fields = ['new_password1', 'new_password2']
class DemandeProlongementForm (forms.ModelForm):
    class Meta:
        model = Demande_prolongement
        fields = '__all__'