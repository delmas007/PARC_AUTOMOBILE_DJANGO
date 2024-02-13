from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

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

    class Meta:
        model = Utilisateur
        fields = '__all__'
