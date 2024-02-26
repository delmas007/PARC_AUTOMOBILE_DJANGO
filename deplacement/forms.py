from django import forms

import deplacement
from Model.models import Deplacement, Vehicule, Utilisateur, Conducteur
from django.db.models import Q
from django.forms import ClearableFileInput
from django.forms.widgets import Input


class MultipleFileInput(Input):
    template_name = 'enregister_deplacement.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context


class DeplacementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeplacementForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })
        self.fields['vehicule'].queryset = Vehicule.objects.exclude(disponibilite=False)

        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule2",
            'required': True,
        })
        self.fields['conducteur'].queryset = Conducteur.objects.exclude(disponibilite=False)
        
    class Meta:
        model = Deplacement
        exclude = ['demande_prolongement_id']

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)


class deplacementModifierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(deplacementModifierForm, self).__init__(*args, **kwargs)
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': False,
        })
        self.fields['vehicule'].queryset = Vehicule.objects.filter(disponibilite=True)

        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectConducteur",
            'required': False,
        })

        self.fields['conducteur'].queryset = Conducteur.objects.filter(disponibilite=True)


    class Meta:
        model = Deplacement
        exclude = ['demande_prolongement_id', 'utilisateur']

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
