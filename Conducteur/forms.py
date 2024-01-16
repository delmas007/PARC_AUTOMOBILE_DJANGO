# nom_de_l_application/forms.py

from django import forms

from Model.models import Conducteur


class ConducteurForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = '__all__'
