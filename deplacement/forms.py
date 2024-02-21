from django import forms

from Model.models import Deplacement
from Model.models import Utilisateur
from Model.models import Vehicule
from Model.models import EtatArrive
from django.db.models import Q

class DeplacementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeplacementForm, self).__init__(*args, **kwargs)
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


        # self.fields['conducteur'].queryset = Utilisateur.objects.exclude(conducteur_id__isnull=True)
        # Filtrer les utilisateurs avec conducteur_id non nul

        # self.fields['utilisateur'].queryset =self.fields['utilisateur'].queryset.exclude(conducteur_id__isnull=True)


    class Meta:
        model = Deplacement
        exclude = ['demande_prolongement_id']
