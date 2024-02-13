from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from Model.forms import ConnexionForm, UserRegistrationForm
from Model.models import Roles


# Create your views here.

class Connexion(LoginView):
    template_name = 'connexion.html'
    form_class = ConnexionForm

    def get_success_url(self) -> str:
        if self.request.user.roles.role == 'EMPLOYER':
            return reverse('employer:reservation')
        elif self.request.user.roles.role == 'ADMIN':
            return reverse('admins:reservation_D')
        elif self.request.user.roles.role == 'CLIENT':
            return reverse('Accueil')
        elif self.request.user.roles.role == 'VENDEUR':
            return reverse('vendeur:ajouter_un_produit')


class Deconnexion(LogoutView):
    pass


@csrf_protect
def inscription(request):
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
            return render(request, 'inscription.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'inscription.html', context=context)
