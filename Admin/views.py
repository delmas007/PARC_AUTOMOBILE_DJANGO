from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from Model.forms import UserRegistrationForm
from Model.models import Roles, Utilisateur


# Create your views here.
@csrf_protect
def inscription(request):
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            client_role = Roles.objects.get(role=Roles.GESTIONNAIRE)
            user.roles = client_role
            # user.is_active = False
            # activateEmail(request, user, form.cleaned_data.get('email'))
            user.save()
            return redirect('admins:Compte_gestionnaire')
        else:

            context['form'] = form
            return render(request, 'ajouter_gestionnaire.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'ajouter_gestionnaire.html', context=context)


# @login_required
def employer_compte(request):
    # if not request.user.roles or request.user.roles.role != 'ADMIN':
    #     return redirect('vitrine:Acces_interdit')

    # Inclure à la fois les rôles "EMPLOYER" et "VENDEUR"
    utilisateurs_gestionnaire = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE])

    return render(request, 'tous_les_gestionnaires.html', {'gestionnaires': utilisateurs_gestionnaire})


# @login_required
def active_emp(request, employer_id):
    # if not request.user.roles or request.user.roles.role != 'ADMIN':
    #     return redirect('vitrine:Acces_interdit')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()

    return redirect('admins:Compte_gestionnaire')


# @login_required
def desactive_amp(request, employer_id):
    # if not request.user.roles or request.user.roles.role != 'ADMIN':
    #     return redirect('vitrine:Acces_interdit')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_gestionnaire')
