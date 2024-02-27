from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from Model.models import Deplacement, Photo, EtatArrive
from deplacement.forms import DeplacementForm, deplacementModifierForm, EtatArriveForm
from datetime import date, timedelta
from django.db.models import Q


def enregistrer_deplacement(request):
    if request.method == 'POST':
        form = DeplacementForm(request.POST)
        if form.is_valid():

            deplacement = form.save(commit=False)
            deplacement.utilisateur = request.user

            # Obtenez l'instance du véhicule associé à ce déplacement (hypothétique)
            vehicule = deplacement.vehicule

            # Obtenez l'instance du conducteur associé à ce déplacement (hypothétique)
            conducteur = deplacement.conducteur

            # Mettez à jour la disponibilité du véhicule
            if vehicule:
                vehicule.disponibilite = False
                vehicule.save()

            # Mettez à jour l'aptitude du conducteur à avoir un véhicule
            if conducteur:
                conducteur.disponibilite = False
                conducteur.save()

            deplacement.save()
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                for uploaded_file in images:
                    photo = Photo.objects.create(deplacement=deplacement, images=uploaded_file)
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')

            messages.success(request, 'Déplacement enregistré avec succès !')
            return redirect('deplacement:enregistrer_deplacement')
    else:
        form = DeplacementForm()

    return render(request, 'enregistrer_deplacement.html', {'form': form})


def liste_deplacement(request):
    aujourd_hui = date.today()
    deplacement = Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui))

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
    aujourd_hui = date.today()
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    deplacement = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))

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
    aujourd_hui = date.today()
    etatarrive = EtatArrive.objects.filter(date_arrive__gte=aujourd_hui - timedelta(days=7)).exclude(
        date_arrive__gt=aujourd_hui)

    paginator = Paginator(etatarrive.order_by('date_mise_a_jour'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        etatarrive = paginator.page(page)
    except EmptyPage:

        etatarrive = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement_arrive.html', {'etatarrives': etatarrive})


def modifier_deplacement(request, pk):
    deplacement = get_object_or_404(Deplacement, pk=pk)
    photos = Photo.objects.filter(deplacement=pk)
    if request.method == 'POST':
        form = deplacementModifierForm(request.POST, request.FILES, instance=deplacement)
        if form.is_valid():
            if request.FILES.getlist('images'):
                Photo.objects.filter(deplacement=deplacement).delete()
                for image in request.FILES.getlist('images'):
                    Photo.objects.create(deplacement=deplacement, images=image)
            form.save()

            return redirect('deplacement:liste_deplacement')
    else:

        form = deplacementModifierForm(instance=deplacement, initial={
            'vehicule': deplacement.vehicule,
            'conducteur': deplacement.conducteur,
            'date_depart': deplacement.date_depart,
            'duree_deplacement': deplacement.duree_deplacement,
            'niveau_carburant': deplacement.niveau_carburant,
            'kilometrage_depart': deplacement.kilometrage_depart,
        })

    return render(request, 'modifier_deplacement.html', {'form': form, 'deplacement': deplacement, 'photos': photos})


def details_deplacement(request, deplacement_id):
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(deplacement=deplacement_id)
    return render(request, 'deplacement_details.html', {'deplacement': deplacement, 'image': image})


def enregistrer_etatArriver(request):
    if request.method == 'POST':
        form = EtatArriveForm(request.POST)
        if form.is_valid():
            etat_arrive = form.save(commit=False)
            etat_arrive.utilisateur = request.user

            deplacement_id = form.cleaned_data['deplacement_id']
            deplacement = Deplacement.objects.get(id=deplacement_id)
            etat_arrive.deplacement = deplacement

            vehicule = etat_arrive.deplacement.vehicule
            conducteur = etat_arrive.deplacement.conducteur

            if vehicule:
                vehicule.disponibilite = True
                vehicule.save()
            if conducteur:
                conducteur.disponibilite = True
                conducteur.save()
            etat_arrive.save()
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                for uploaded_file in images:
                    photo = Photo.objects.create(etat_arrive=etat_arrive, images=uploaded_file)
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')
            messages.success(request, 'Déplacement enregistré avec succès !')
            return redirect('deplacement:liste_deplacement_en_cours')
        else:
            print(form.errors)
    else:
        form = EtatArriveForm()

    context = {'form': form}
    return render(request, 'afficher_deplacement_en_cours.html', context)


def details_arriver(request, etatarrive_id):
    etat_arrive = get_object_or_404(EtatArrive, id=etatarrive_id)
    deplacement_id = etat_arrive.deplacement.id
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(etat_arrive=etatarrive_id)
    images = Photo.objects.filter(deplacement=deplacement_id)
    return render(request, 'arriver_details.html', {'etat_arrive': etat_arrive, 'deplacement': deplacement, 'image': image, 'images': images})
