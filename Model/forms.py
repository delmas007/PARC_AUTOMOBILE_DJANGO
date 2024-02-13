from django.contrib.auth.forms import AuthenticationForm

from Model.models import Utilisateur


class ConnexionForm(AuthenticationForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'style': "color: black;",
            'id': "email",
            'placeholder': "name@example.com",
            'required': '',
            'pattern': '[^ @]*@[^ @]*',
            'name': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'type': "password",
            'name': 'password',
            'class': "form-control ",
            'style': "color: black;",
            'id': "password",
            'placeholder': "Password",
        })

class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'type': "email",
            'class': "form-control",
            'style': "color: black;",
            'id': "email",
            'placeholder': "name@example.com",
            'required': '',
            'pattern': '[^ @]*@[^ @]*',
            'name': 'email',
        })
        self.fields['nom'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'style': "color: black;",
            'id': "nom",
            'placeholder': "Nom",
            'required': '',
            'name': 'nom',
        })
        self.fields['prenom'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'style': "color: black;",
            'id': "prenom",
            'placeholder': "prenom",
            'required': '',
            'name': 'prenom',
        })
        self.fields['contact'].widget.attrs.update({
            'type': "number",
            'class': "form-control",
            'style': "color: black;",
            'id': "contact",
            'placeholder': "0715226698",
            'required': '',
            'name': 'contact',
        })
        self.fields['commune'].widget.attrs.update({
            'type': "text",
            'class': "form-control",
            'style': "color: black;",
            'id': "commune",
            'placeholder': "abidjan",
            'required': '',
            'name': 'commune',
        })
        self.fields['sexe'].widget.attrs.update({
            'name': "sexe",
            'style': "color: #212529;",
            'class': "form-select",
            'id': "sexe",
        })
        self.fields['password1'].widget.attrs.update({
            'type': "password",
            'name': 'password',
            'class': "form-control ",
            'style': "color: black;",
            'id': "password",
            'placeholder': "Password",
        })
        self.fields['password2'].widget.attrs.update({
            'type': "password",
            'name': 'password',
            'class': "form-control ",
            'style': "color: black;",
            'id': "password",
            'placeholder': "Confirme Password",
        })

    class Meta:
        model = Utilisateur
        fields = ('email', 'nom', 'prenom', 'contact', 'commune', 'sexe')