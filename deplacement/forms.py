from django import forms

from Model.models import Deplacement


class DeplacementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })
        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule2",
            'required': True,
        })

    class Meta:
        model = Deplacement
        exclude = ['statut', 'date_depart', 'date_depart', 'date_arrivee', 'depart', 'arrivee']
