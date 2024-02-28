from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.forms.widgets import Input

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


class MultipleFileInput(Input):
    template_name = 'compte_conducteur.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context


class DemandeProlongementForm(forms.ModelForm):
    class Meta:
        model = Demande_prolongement
        fields = ['motif', 'duree']
        images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
