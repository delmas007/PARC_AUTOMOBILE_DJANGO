from django import forms

from Model.models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['description_incident', 'vehicule']