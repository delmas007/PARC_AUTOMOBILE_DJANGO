from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, ExpressionWrapper, fields, F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from oscrypto._ffi import null

from Admin.forms import typeCarburantForm, CarburantModifierForm, CarburantSearchForm, UserRegistrationForm
from Conducteur.forms import ConducteurSearchForm
from Model.models import Roles, Utilisateur, type_carburant, periode_carburant
from vehicule.forms import VehiculSearchForm


@csrf_protect
def inscription(request):
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            client_role = Roles.objects.get(role=Roles.GESTIONNAIRE)
            user.roles = client_role
            user.save()
            # Récupérez l'URL de l'image téléchargée
            image_url = user.image.url if user.image else None
            # Ajoutez l'URL de l'image au contexte
            context['user_image_url'] = image_url
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
    return render(request, 'tous_les_gestionnairess.html', {'gestionnaires2': gestionnaires2})


# @login_required
def active_emp(request, employer_id):
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()
    return redirect('admins:gestionnaire_inactifs')


def desactive_amp(request, employer_id):
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_gestionnaire')


def gestionnaire_a_search(request):
    form = VehiculSearchForm(request.GET)
    gestionnaire = Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=False)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        context = {'gestionnaires': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnaires.html', context)


def gestionnaire_a_search_i(request):
    form = VehiculSearchForm(request.GET)
    gestionnaire = Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=True)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        context = {'gestionnaires2': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnairess.html', context)


def Ajouter_Carburant(request):
    if request.method == 'POST':
        form = typeCarburantForm(request.POST)
        print(request.POST.get("nom"))
        carburant_id=request.POST.get("nom")
        carburant_prix=request.POST.get("prix")
        if form.is_valid():

            carburant=type_carburant.objects.get(id=carburant_id)
            carburant.prix=carburant_prix
            carburant.save()
            dernier_periode = periode_carburant.objects.filter(carburant=carburant).order_by('-date_debut').first()
            if dernier_periode:
                date_fin = dernier_periode.date_debut
                periode = periode_carburant.objects.create(carburant=carburant,date_debut=carburant.date_mise_a_jour,prix=carburant.prix)
                dernier_periode.date_fin=date_fin
                dernier_periode.save()
                periode.save()
            else:
                periode = periode_carburant.objects.create(carburant=carburant, date_debut=carburant.date_mise_a_jour,
                                                           prix=carburant.prix)
                periode.save()
            messages.success(request, "Carburant ajouté avec succès.")
            return redirect('admins:Ajouter_Carburant')
        else:
            print(form.errors)
    else:
        form = typeCarburantForm()
    return render(request, 'enregistrer_carburant.html', {'form': form})


def liste_Carburant(request):
    carburant_list =(
        type_carburant.objects.all()
        .annotate(hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField()))
        .order_by('-hour')
    )

    paginator = Paginator(carburant_list, 5)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        carburants = paginator.page(page)
    except EmptyPage:

        carburants = paginator.page(paginator.num_pages())

    return render(request, 'afficher_carburant.html', {'carburants': carburants})

def Carburant_search(request):
    form = CarburantSearchForm(request.GET)
    carburant = type_carburant.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            carburant = carburant.filter(Q(nom__icontains=query))

        context = {'carburants': carburant, 'form': form}
        paginator = Paginator(carburant.order_by('-date_mise_a_jour'), 5)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            carburants = paginator.page(page)
        except EmptyPage:
            carburants = paginator.page(paginator.num_pages())
        context = {'carburants': carburants, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not carburant.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_carburant.html', context)


def modifier_carburant(request, pk):
    carburant = get_object_or_404(type_carburant, pk=pk)

    if request.method == 'POST':
        form = CarburantModifierForm(request.POST, request.FILES, instance=carburant)
        if form.is_valid():
            form.instance.utilisateur = request.user
            form.save()

            return redirect('admins:liste_Carburant')
    else:
        form = CarburantModifierForm(instance=carburant)

    return render(request, 'modifier_carburants.html', {'form': form, 'entretien': carburant, })


def dashboard_admins(request):
    return render(request, 'dashoard_admins.html')
