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

        # Récupérer l'instance de déplacement actuelle
        instance = kwargs.get('instance')

        # Définir le queryset pour le champ 'vehicule'
        if instance:
            # Si une instance existe (modification), inclure le véhicule/le conducteur actuel
            vehicule_actuel = instance.vehicule
            conducteur_actuel = instance.conducteur
            self.fields['vehicule'].queryset = Vehicule.objects.filter(Q(disponibilite=True) | Q(pk=vehicule_actuel.pk))
            self.fields['conducteur'].queryset = Conducteur.objects.filter(Q(disponibilite=True) | Q(pk=conducteur_actuel.pk))
        else:
            # Si aucune instance n'existe (ajout), afficher tous les véhicules/conducteurs disponibles
            self.fields['vehicule'].queryset = Vehicule.objects.filter(disponibilite=True)
            self.fields['conducteur'].queryset = Conducteur.objects.filter(disponibilite=True)

        # Mise à jour des attributs du widget 'vehicule'
        self.fields['vehicule'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule",
            'required': True,
        })

        # Mise à jour des attributs du widget 'conducteur'
        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectVehicule2",
            'required': True,
        })

        # Exclure les conducteurs non disponibles


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
            'required': True,
        })

        self.fields['conducteur'].widget.attrs.update({
            'class': "form-control",
            'id': "selectConducteur",
            'required': True,
        })


    class Meta:
        model = Deplacement
        exclude = ['demande_prolongement_id', 'utilisateur']

    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
