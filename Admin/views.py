from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from Model.forms import UserRegistrationForm
from Model.models import Roles, Utilisateur


@csrf_protect
def inscription(request):
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            client_role = Roles.objects.get(role=Roles.GESTIONNAIRE)
            user.roles = client_role
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
    gestionnaires = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=True)

    return render(request, 'tous_les_gestionnaires.html', {'gestionnaires': gestionnaires})


def gestionnaire_inactifs(request):
    gestionnaires2 = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=False)
    return render(request, 'tous_les_gestionnaires.html', {'gestionnaires2': gestionnaires2})


# @login_required
def active_emp(request, employer_id):
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()

    return redirect('admins:Compte_gestionnaire')


def desactive_amp(request, employer_id):
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_gestionnaire')
