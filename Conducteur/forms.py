# nom_de_l_application/forms.py

from django import forms

from Model.models import Conducteur


class ConducteurForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        exclude = ['disponibilite','supprimer']

    def __init__(self, *args, **kwargs):
        super(ConducteurForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'disponibilite' and field_name != 'image':
                self.fields[field_name].required = True


class ConducteurSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un conducteur: Nom, Prenom, Numero...', 'class': 'form-control conducteur-search'}),
    )
