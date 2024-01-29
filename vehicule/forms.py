from django import forms

from Model.models import Vehicule


class XYZ_DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({
            'class': 'form-control',
            'required': False,
        })
        kwargs["format"] = "%m-%d-%Y"
        # kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)


class XYZ_DateInpute(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({
            'class': 'form-control',
            'required': False,
        })
        kwargs["format"] = "%m-%d-%Y"
        # kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)


class VehiculeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['marque'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "marque",
            'placeholder': "Entrez la marque du vehicule",
            'required': True,
            'name': 'marque',
        })
        self.fields['modele'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "modele",
            'placeholder': "Entrez le modele du vehicule",
            'required': True,
            'name': 'modele',
        })
        self.fields['couleur'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "couleur",
            'placeholder': "Entrez la couleur du vehicule",
            'required': False,
            'name': 'couleur',
        })
        self.fields['numero_immatriculation'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "marque",
            'placeholder': "Entrez le numero d'immatriculation du vehicule",
            'required': True,
            'name': 'marque',
        })
        self.fields['type_carburant'].widget.attrs.update({
            'class': "form-control",
            'id': "exampleFormControlSelect1",
            'placeholder': "Entrez la marque du vehicule",
            'required': False,
        })
        self.fields['kilometrage'].widget.attrs.update({
            'type': "number",
            'class': "form-control",
            'id': "marque",
            'required': False,
            'name': 'kilometrage',
        })
        self.fields['image'].widget.attrs.update({
            'type': "file",
            'class': "form-control",
            'id': "marque",
            'required': True,
            'name': 'image',
        })

    class Meta:
        model = Vehicule
        fields = ['marque', 'modele', 'couleur', 'numero_immatriculation', 'date_mise_en_service', 'annee_fabrication',
                  'type_carburant', 'kilometrage', 'image']

        widgets = {
            'date_mise_en_service': XYZ_DateInput(attrs={'id': 'date'}),
            'annee_fabrication': XYZ_DateInput(attrs={'id': 'date'}),
        }


class VehiculeForme(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['marque'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "marque",
            'placeholder': "Entrez la marque du vehicule",
            'required': True,
            'name': 'marque',
        })
        self.fields['modele'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "modele",
            'placeholder': "Entrez le modele du vehicule",
            'required': True,
            'name': 'modele',
        })
        self.fields['couleur'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "couleur",
            'placeholder': "Entrez la couleur du vehicule",
            'required': True,
            'name': 'couleur',
        })
        self.fields['numero_immatriculation'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'id': "marque",
            'placeholder': "Entrez le numero d'immatriculation du vehicule",
            'required': True,
            'name': 'marque',
        })
        self.fields['type_carburant'].widget.attrs.update({
            'class': "form-control",
            'id': "exampleFormControlSelect1",
            'placeholder': "Entrez la marque du vehicule",
            'required': False,
        })
        self.fields['kilometrage'].widget.attrs.update({
            'type': "number",
            'class': "form-control",
            'id': "marque",
            'required': True,
            'name': 'kilometrage',
        })
        self.fields['image'].widget.attrs.update({
            'type': "file",
            'class': "form-control",
            'id': "marque",
            'required': False,
            'name': 'image',
        })

    class Meta:
        model = Vehicule
        fields = ['marque', 'modele', 'couleur', 'numero_immatriculation', 'date_mise_en_service', 'annee_fabrication',
                  'type_carburant', 'kilometrage', 'image']


class VehiculSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un vehicul: Marque, model, matricule...', 'class': 'form-control'}),
    )
