from django import forms
from django.forms import ClearableFileInput
from django.forms.widgets import Input

from Model.models import Vehicule, Marque


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


class MultipleFileInput(Input):
    template_name = 'ajouter_vehicule.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value
        return context


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'

    marque = forms.ModelChoiceField(queryset=Marque.objects.all(), required=True)
    images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)
    energie = forms.ChoiceField(choices=Vehicule._meta.get_field('energie').choices, required=True)

    def __init__(self, *args, **kwargs):
        super(VehiculeForm, self).__init__(*args, **kwargs)
        self.fields['marque'].widget.attrs.update({
            'class': "form-control",
            'id': "selectMarque",
            'required': True,
        })
        self.fields['date_d_edition'].required = True
        self.fields['date_expiration_assurance'].required = True
        self.fields['date_videnge'].required = True
        # self.fields['type_commercial'].required = True
        self.fields['date_mise_circulation'].required = True
        self.fields['energie'].widget.attrs.update({
            'class': "form-control",
            'id': "energie",
            'required': True,
        })
        self.fields['place_assises'].widget.attrs.update({
            'class': "form-control",
            'id': "place_assises",
            'required': True,
        })
        self.fields['carrosserie'].widget.attrs.update({
            'class': "form-control",
            'id': "carrosserie",
            'required': True,
        })
        self.fields['numero_immatriculation'].widget.attrs.update({
            'class': "form-control",
            'id': "numero_immatriculation",
            'required': True,
        })
        self.fields['kilometrage'].widget.attrs.update({
            'class': "form-control",
            'id': "kilometrage",
            'required': True,
        })
        self.fields['carte_grise'].widget.attrs.update({
            'class': "form-control",
            'id': "carte_grise",
            'required': True,
        })
        self.fields['couleur'].widget.attrs.update({
            'class': "form-control",
            'id': "couleur",
            'required': True,
        })


class VehiculSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un vehicul: Marque, model, matricule...', 'class': 'form-control'}),
    )


class marqueForm(forms.ModelForm):
    class Meta:
        model = Marque
        fields = '__all__'
