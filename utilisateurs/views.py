from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from Model.forms import UserRegistrationForm, ConnexionForm
from Model.models import Roles, Utilisateur
from utilisateurs.forms import ConducteurClientForm


# Create your views here.

def Accueil_user(request):
    return render(request, 'index_user.html')


def Compte(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            utilisateur = Utilisateur.objects.get(username=request.user.username)
            conducteur_form = ConducteurClientForm(request.POST, request.FILES)
            if conducteur_form.is_valid():
                conducteur_instance = conducteur_form.save()
                utilisateur.conducteur = conducteur_instance
                utilisateur.save()
                messages.success(request, 'Le conducteur a été ajouté avec succès.')
                return redirect('utilisateur:compte')
            else:
                print(conducteur_form.errors)
        else:
            return redirect('login')  # Rediriger vers la page de connexion si l'utilisateur n'est pas authentifié
    else:
        conducteur_form = ConducteurClientForm()

    return render(request, 'compte.html', {'conducteur_form': conducteur_form})

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
            return redirect('utilisateur:Accueil_user')
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
