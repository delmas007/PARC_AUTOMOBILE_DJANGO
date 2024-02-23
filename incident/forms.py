from django import forms
from Model.models import Incident


class IncidentFormGestionnaire(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['description_incident', 'vehicule', 'utilisateurs']

    def __init__(self, *args, **kwargs):
        super(IncidentFormGestionnaire, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })

        #####VALIDATION, AFFICHAGE D ERREUR
        self.fields['description_incident'].error_messages = {
            'required': " Le champ Description de l'incident est obligatoire."
        }



