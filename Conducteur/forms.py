# nom_de_l_application/forms.py

from django import forms

from Model.models import Conducteur


class ConducteurForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ConducteurForm, self).__init__(*args, **kwargs)
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['numero_telephone'].required = True
        self.fields['numero_permis_conduire'].required = True


class ConducteurSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Rechercher un conducteur: Nom, Prenom, Numero...', 'class': 'form-control'}),
    )
