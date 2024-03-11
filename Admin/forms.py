from django import forms

from Model.models import type_carburant


class typeCarburantForm(forms.ModelForm):
    class Meta:
        model = type_carburant
        fields = ['nom', 'prix']


# class CarburantModifierForm(forms.ModelForm):
#     class Meta:
#         model = type_carburant
#         fields = ['nom', 'prix']


class CarburantModifierForm(forms.ModelForm):
    class Meta:
        model = type_carburant
        fields = ['nom', 'prix']

    def __init__(self, *args, **kwargs):
        super(CarburantModifierForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control', 'id': 'exampleInputdate'})
        self.fields['prix'].widget.attrs.update({'class': 'form-control', 'min': '1'})
