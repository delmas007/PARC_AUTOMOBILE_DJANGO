
from django import forms

from Model.models import Carburant


class AjouterCarburantForm(forms.ModelForm):
    class Meta:
        model = Carburant
        fields = ['vehicule', 'type', 'quantite']

    def __init__(self, *args, **kwargs):
        super(AjouterCarburantForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({'class': 'form-control', 'id': 'selectVehicule'})
        self.fields['type'].widget.attrs.update({'class': 'form-control', 'id': 'selectType'})
        self.fields['quantite'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ajouter le litre de carburant', 'min': '1', 'required': 'required'})

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        return quantite


class ModifierCarburantForm(forms.ModelForm):
    class Meta:
        model = Carburant
        fields = ['vehicule', 'type', 'quantite']

    def __init__(self, *args, **kwargs):
        super(ModifierCarburantForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantite'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ajouter le litre de carburant ', 'min': '1', 'required': 'required'})

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        # Ajoutez ici d'autres validations personnalisées selon vos besoins
        return quantite