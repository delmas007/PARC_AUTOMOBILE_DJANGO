from django import forms

from Model.models import type_carburant


class typeCarburantForm(forms.ModelForm):
    class Meta:
        model = type_carburant
        fields = '__all__'
