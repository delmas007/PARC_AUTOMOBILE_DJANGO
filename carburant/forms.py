
from django import forms


class CarburantForm(forms.Form):
    nom = forms.CharField(label='Nom du carburant', max_length=100)
    prix = forms.IntegerField(label='Prix du litre du carburant', min_value=1)
