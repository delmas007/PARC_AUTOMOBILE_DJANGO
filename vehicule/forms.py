from django import forms

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


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'

    marque = forms.ModelChoiceField(queryset=Marque.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(VehiculeForm, self).__init__(*args, **kwargs)
        self.fields['marque'].required = True
        self.fields['kilometrage'].required = True
        self.fields['date_d_edition'].required = True
        self.fields['image'].required = True
        self.fields['carte_grise'].required = True
        self.fields['date_expiration_assurance'].required = True
        self.fields['date_videnge'].required = True
        self.fields['type_commercial'].required = True


class VehiculSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Rechercher un vehicul: Marque, model, matricule...', 'class': 'form-control'}),
    )
