from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Model.forms import UserRegistrationForm, UserRegistrationForme, UserRegistrationFormee
from Model.models import Conducteur, Roles, Utilisateur
from .forms import ConducteurForm, ConducteurSearchForm


def ajouter_conducteur(request):
    if request.method == 'POST':
        conducteur_form = ConducteurForm(request.POST, request.FILES)
        utilisateur_form = UserRegistrationForme(request.POST)
        if conducteur_form.is_valid() and utilisateur_form.is_valid():
            conducteur_instance = conducteur_form.save()
            utilisateur_instance = utilisateur_form.save(commit=False)
            utilisateur_role = Roles.objects.get(role=Roles.CONDUCTEUR)
            utilisateur_instance.roles = utilisateur_role
            utilisateur_instance.conducteur = conducteur_instance
            utilisateur_instance.save()
            messages.success(request, 'Le conducteur a été ajouté avec succès.')
            return redirect('conducteur:ajouter_conducteur')
        else:
            print(conducteur_form.errors)
            print(utilisateur_form.errors)
    else:
        conducteur_form = ConducteurForm()
        utilisateur_form = UserRegistrationForme()

    return render(request, 'ajouter_conducteur.html',
                  {'conducteur_form': conducteur_form, 'utilisateur_form': utilisateur_form})


def tous_les_conducteurs(request):
    conducteurs = Conducteur.objects.all().order_by('utilisateur__nom')
    utilisateurs = Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True)

    items_per_page = 5
    paginator = Paginator(conducteurs, items_per_page)
    page = request.GET.get('page')

    try:
        conducteurs = paginator.page(page)
    except PageNotAnInteger:
        conducteurs = paginator.page(1)
    except EmptyPage:
        conducteurs = paginator.page(paginator.num_pages)

    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs, 'utilisateurs': utilisateurs})


def supprimer_conducteur(request, conducteur_id):
    utilisateurs = get_object_or_404(Utilisateur, conducteur=conducteur_id)
    utilisateurs.is_active = False
    utilisateurs.save()
    return redirect('conducteur:tous_les_conducteurs')


def modifier_conducteur(request, conducteur_id):
    global form
    conducteur = get_object_or_404(Conducteur, pk=conducteur_id)
    utilisateur = get_object_or_404(Utilisateur, conducteur=conducteur_id)
    if request.method == 'POST':
        form_conducteur = ConducteurForm(request.POST, request.FILES, instance=conducteur)
        form_utilisateur = UserRegistrationFormee(request.POST, instance=utilisateur)
        if form_conducteur.is_valid() and form_utilisateur.is_valid():
            conducteur = form_conducteur.save(commit=False)
            nouveau_fichier = request.FILES.get('image', None)
            if nouveau_fichier:
                conducteur.image = nouveau_fichier
            conducteur.save()
            form_utilisateur.save()
            return redirect('conducteur:tous_les_conducteurs')
    else:
        form = ConducteurForm(instance=conducteur, initial={
            'date_de_naissance': conducteur.date_de_naissance,
            'date_embauche': conducteur.date_embauche,
        })
    return render(request, 'modifier_conducteur.html',
                  {'form': form, 'conducteur': conducteur, 'utilisateur': utilisateur})


def conducteur_search(request):
    form = ConducteurSearchForm(request.GET)
    conducteurs = Conducteur.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            conducteurs = conducteurs.filter(
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(numero_telephone__icontains=query)
            )

    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs, 'search_form': form})


def details_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)
    utilisateur = get_object_or_404(Utilisateur, conducteur=conducteur_id)
    return render(request, 'conducteur_details.html', {'conducteur': conducteur, 'utilisateur': utilisateur})
