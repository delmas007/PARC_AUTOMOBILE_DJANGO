from django.contrib.auth.forms import PasswordResetForm

from Model.models import Conducteur, Utilisateur
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
