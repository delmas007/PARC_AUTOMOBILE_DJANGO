from django import forms

from Model.models import Entretien


class EntretienForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })

    class Meta:
        model = Entretien
        fields = '__all__'
