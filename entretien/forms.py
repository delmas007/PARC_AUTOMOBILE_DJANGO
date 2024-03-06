from django import forms

from Model.models import Entretien


class EntretienForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = '__all__'
