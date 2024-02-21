from Model.models import Conducteur
from django import forms


# Create your models here.

class ConducteurClientForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = '__all__'
