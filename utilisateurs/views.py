from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from Model.forms import UserRegistrationForm, ConnexionForm
from Model.models import Roles


# Create your views here.

def Accueil_user(request):
    return render(request, 'index_user.html')


@csrf_protect
def inscription_user(request):
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            client_role = Roles.objects.get(role=Roles.CLIENT)
            user.roles = client_role
            # user.is_active = False
            # activateEmail(request, user, form.cleaned_data.get('email'))
            user.save()
            return redirect('Model:connexion')
        else:

            context['form'] = form
            return render(request, 'inscription_client.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'inscription_client.html', context=context)


class Connexion_user(LoginView):
    template_name = 'connexion_user.html'
    form_class = ConnexionForm

    def get_success_url(self) -> str:
        if self.request.user.roles.role == 'CLIENT':
            return reverse('utilisateur:Accueil_user')
        if self.request.user.roles.role == 'CONDUCTEUR':
            return reverse('utilisateur:Accueil_user')
