from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from Model.models import Deplacement
from deplacement.forms import DeplacementForm


def enregistrer_deplacement(request):
    if request.method == 'POST':
        form = DeplacementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicule ajouté avec succès !')
            return redirect('deplacement:enregistrer_deplacement')
    else:
        form = DeplacementForm()

    return render(request, 'enregistrer_deplacement.html', {'form': form})


def liste_deplacement(request):
    deplacement = Deplacement.objects.filter(depart=False, arrivee=False)

    paginator = Paginator(deplacement.order_by('date_mise_a_jour'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        deplacement = paginator.page(page)
    except EmptyPage:

        deplacement = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement.html', {'deplacements': deplacement})


def depart(request, pk):
    deplacement = get_object_or_404(Deplacement, pk=pk)
    deplacement.depart = True
    deplacement.statut = 'en cours'
    deplacement.save()  # Ligne corrigée
    return redirect('deplacement:liste_deplacement')


def liste_deplacement_en_cours(request):
    deplacement = Deplacement.objects.filter(depart=True, arrivee=False)
    paginator = Paginator(deplacement.order_by('date_mise_a_jour'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        deplacement = paginator.page(page)
    except EmptyPage:

        deplacement = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement_en_cours.html', {'deplacements': deplacement})


def arrivee(request, pk):
    deplacement = get_object_or_404(Deplacement, pk=pk)
    deplacement.arrivee = True
    deplacement.statut = 'arrivée'
    deplacement.save()  # Ligne corrigée
    return redirect('deplacement:liste_deplacement_en_cours')


def liste_deplacement_arrive(request):
    today = datetime.now()
    deplacement = Deplacement.objects.filter(depart=True, arrivee=True, date_arrivee__date=today)

    paginator = Paginator(deplacement.order_by('date_mise_a_jour'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        deplacement = paginator.page(page)
    except EmptyPage:

        deplacement = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement_arrive.html', {'deplacements': deplacement})
