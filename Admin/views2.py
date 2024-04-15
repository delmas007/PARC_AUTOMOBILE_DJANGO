import calendar
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, ExpressionWrapper, fields, F, Sum, Subquery
from django.utils.translation import gettext as french
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Model.models import Vehicule, Carburant, Entretien, Incident, Conducteur, EtatArrive, Photo, Deplacement
from deplacement.forms import DeplacementSearchForm
from incident.forms import IncidentSearchForm


@login_required(login_url='Connexion')
def courbe_depense_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        prix_carburant = Carburant.objects.filter(date_premiere__month=mois, date_premiere__year=annee)
        prix_entretien = Entretien.objects.filter(date_entretien__month=mois, date_entretien__year=annee)
        # Calculer la consommation de carburant pour chaque véhicule
        prix_par_vehicule = {}
        for prix in prix_carburant:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_total

        # Parcourir la liste des prix d'entretien
        for prix in prix_entretien:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_entretient
        labels = []
        data = []
        for vehicule, prix in prix_par_vehicule.items():
            labels.append(f"{vehicule}")
            data.append(prix)

        return render(request, 'rapport_depense_mensuel.html',
                      {'labels': labels, 'data': data, 'vehicule': voiture, 'mois': mois_lettre, 'annee': annee})

    return render(request, 'rapport_depense_mensuel.html')


@login_required(login_url='Connexion')
def courbe_depense_global(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        debut = request.POST.get('date_debut_periode')
        fin = request.POST.get('date_fin_periode')
        debut_date = datetime.strptime(debut, '%Y-%m-%d').date()

        if fin:
            fin_date = datetime.strptime(fin, '%Y-%m-%d').date()
        else:
            fin_date = date.today()

        vehicules = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        prix_carburant = Carburant.objects.filter(date_premiere__range=(debut_date, fin_date))
        prix_entretien = Entretien.objects.filter(date_entretien__range=(debut_date, fin_date))
        # Calculer la consommation de carburant pour chaque véhicule
        prix_par_vehicule = {}
        for prix in prix_carburant:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_total

        # Parcourir la liste des prix d'entretien
        for prix in prix_entretien:
            if prix.vehicule not in prix_par_vehicule:
                prix_par_vehicule[prix.vehicule] = 0
            prix_par_vehicule[prix.vehicule] += prix.prix_entretient
        labels = []
        data = []
        for vehicule, prix in prix_par_vehicule.items():
            labels.append(f"{vehicule}")
            data.append(prix)

        return render(request, 'rapport_depense.html',
                      {'labels': labels, 'data': data, 'vehicule': vehicules, 'debut': debut_date, 'fin': fin_date})

    return render(request, 'rapport_depense.html')


@login_required(login_url='Connexion')
def courbe_entretien_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        vehicules_ids_with_carburant = Entretien.objects.values(
            'vehicule_id').distinct()
        vehicles = Vehicule.objects.filter(id__in=Subquery(vehicules_ids_with_carburant))
        voiture = Vehicule.objects.all()
        labels = [f"{vehicle}" for vehicle in vehicles]
        fuel_data = [vehicle.total_entretien(mois, annee) for vehicle in vehicles]
        quantites = [data['quantite'] for data in fuel_data]
        prix = [data['prix'] for data in fuel_data]

        context = {
            'labels': labels,
            'quantites': quantites,
            'prix': prix,
            'mois': mois_lettre,
            'annee': annee,
            'vehicules': voiture,
        }

        return render(request, 'rapport_entretien_mensuel.html', context)

    return render(request, 'rapport_entretien_mensuel.html')


@login_required(login_url='Connexion')
def courbe_incident_vehicule_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        nbre_incident = Incident.objects.filter(date_premiere__month=mois, date_premiere__year=annee)

        # Calculer la consommation de carburant pour chaque véhicule
        incident_par_vehicule = {}
        for incident in nbre_incident:
            if incident.vehicule not in incident_par_vehicule:
                incident_par_vehicule[incident.vehicule] = 0
            incident_par_vehicule[incident.vehicule] += 1
        labels = []
        data = []
        for vehicule, incident in incident_par_vehicule.items():
            labels.append(f"{vehicule}")
            data.append(incident)

        return render(request, 'rapport_incident_vehicule_mensuel.html',
                      {'labels': labels, 'data': data, 'vehicules': voiture, 'mois': mois_lettre, 'annee': annee})

    return render(request, 'rapport_incident_vehicule_mensuel.html')


@login_required(login_url='Connexion')
def courbe_incident_conducteur_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        conducteurs = Conducteur.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        nbre_incident = Incident.objects.filter(conducteur__isnull=False, date_premiere__month=mois,
                                                date_premiere__year=annee)

        # Calculer la consommation de carburant pour chaque véhicule
        incident_par_conducteur = {}
        for incident in nbre_incident:
            if incident.conducteur not in incident_par_conducteur:
                incident_par_conducteur[incident.conducteur] = 0
            incident_par_conducteur[incident.conducteur] += 1
        labels = []
        data = []
        for conducteur, incident in incident_par_conducteur.items():
            labels.append(f"{conducteur}")
            data.append(incident)

        return render(request, 'rapport_incident_conducteur_mensuel.html',
                      {'labels': labels, 'data': data, 'conducteurs': conducteurs, 'mois': mois_lettre, 'annee': annee})

    return render(request, 'rapport_incident_conducteur_mensuel.html')


@login_required(login_url='Connexion')
def liste_deplacement_arrive_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    etatarrive = (
        EtatArrive.objects.all().annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    paginator = Paginator(etatarrive, 15)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        etatarrive = paginator.page(page)
    except EmptyPage:

        etatarrive = paginator.page(paginator.num_pages())
    return render(request, 'afficher_deplacement_arrive_admin.html', {'etatarrives': etatarrive})


@login_required(login_url='Connexion')
def details_arriver_admin(request, etatarrive_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    etat_arrive = get_object_or_404(EtatArrive, id=etatarrive_id)
    deplacement_id = etat_arrive.deplacement.id
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)
    image = Photo.objects.filter(etat_arrive=etatarrive_id)
    images = Photo.objects.filter(deplacement=deplacement_id)
    return render(request, 'arriver_details_admin.html',
                  {'etat_arrive': etat_arrive, 'deplacement': deplacement, 'image': image, 'images': images})


@login_required(login_url='Connexion')
def liste_incidents_externe_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    aujourd_hui = date.today()
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}
    for item_incident in incidents_list:
        latest_photo = get_latest_photo(item_incident)
        incidents[item_incident.id] = {'incident': item_incident, 'latest_photo': latest_photo}
    paginator = Paginator(list(incidents.values()), 15)
    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    return render(request, 'Liste_incidents_externe_admin.html', {'incidents': incidents_page, 'paginator': paginator})


@login_required(login_url='Connexion')
def liste_incidents_interne_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}
    for item_incident in incidents_list:
        latest_photo = get_latest_photo(item_incident)
        incidents[item_incident.id] = {'incident': item_incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 15)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    return render(request, 'Liste_incidents_interne_admin.html', {'incidents': incidents_page, 'paginator': paginator})


@login_required(login_url='Connexion')
def incident_interne_detail_admin(request, pk):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    incident = get_object_or_404(Incident, id=pk)
    image = Photo.objects.filter(incident=incident)
    return render(request, 'incident_interne_details_admin.html', {'incident': incident, 'image': image})


@login_required(login_url='Connexion')
def incident_externe_detail_admin(request, pk):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    incident = get_object_or_404(Incident, id=pk)
    image = Photo.objects.filter(incident=incident)
    return render(request, 'incident_externe_details_admin.html', {'incident': incident, 'image': image})


def get_latest_photo(incident):
    return Photo.objects.filter(incident=incident).order_by('-id').first()


@login_required(login_url='Connexion')
def incidents_search(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    form = IncidentSearchForm(request.GET)
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            incidents_list = incidents_list.filter(Q(vehicule__numero_immatriculation__icontains=query) |
                                                   Q(description_incident__icontains=query) |
                                                   Q(vehicule__marque__marque__icontains=query))
    for incident in incidents_list:
        latest_photo = get_latest_photo(incident)
        incidents[incident.id] = {'incident': incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 15)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    context = {'incidents': incidents_page, 'form': form, 'paginator': paginator}
    if not incidents and form.is_valid():
        context['no_results'] = True
    return render(request, 'Liste_incidents_interne_admin.html', context)


@login_required(login_url='Connexion')
def incidents_externe_search(request):
    form = IncidentSearchForm(request.GET)
    incidents_list = (
        Incident.objects.filter(conducteur_id__isnull=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )
    incidents = {}

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)
                incidents_list = incidents_list.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(description_incident__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=nom)
                )
                for prenom in prenoms:
                    incidents_list = incidents_list.filter(conducteur__utilisateur__prenom__icontains=prenom)
            else:

                incidents_list = incidents_list.filter(Q(vehicule__numero_immatriculation__icontains=query) |
                                                       Q(description_incident__icontains=query) |
                                                       Q(vehicule__marque__marque__icontains=query) |
                                                       Q(conducteur__utilisateur__nom__icontains=query) |
                                                       Q(conducteur__utilisateur__prenom__icontains=query))
    for incident in incidents_list:
        latest_photo = get_latest_photo(incident)
        incidents[incident.id] = {'incident': incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 15)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    context = {'incidents': incidents_page, 'form': form, 'paginator': paginator}
    # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
    if not incidents and form.is_valid():
        context['no_results'] = True
    return render(request, 'Liste_incidents_externe_admin.html', context)


def arrive_search(request):
    form = DeplacementSearchForm(request.GET)
    arrivee = (
        EtatArrive.objects.annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())
        ).order_by('-hour')
    )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)

                arrivee = arrivee.filter(
                    Q(deplacement__vehicule__marque__marque__icontains=query) |
                    Q(deplacement__vehicule__numero_immatriculation__icontains=query) |
                    Q(deplacement__vehicule__type_commercial__modele__icontains=query) |
                    Q(deplacement__conducteur__utilisateur__nom__icontains=nom)
                )
                for prenom in prenoms:
                    arrivee = arrivee.filter(deplacement__conducteur__utilisateur__prenom__icontains=prenom)

            else:
                # Si la requête ne contient pas exactement deux parties, recherchez normalement
                arrivee = arrivee.filter(
                    Q(deplacement__vehicule__marque__marque__icontains=query) |
                    Q(deplacement__vehicule__numero_immatriculation__icontains=query) |
                    Q(deplacement__vehicule__type_commercial__modele__icontains=query) |
                    Q(deplacement__conducteur__utilisateur__nom__icontains=query) |
                    Q(deplacement__conducteur__utilisateur__prenom__icontains=query)
                )

    paginator = Paginator(arrivee, 15)
    page = request.GET.get("page", 1)
    try:
        etatarrives = paginator.page(page)
    except EmptyPage:
        etatarrives = paginator.page(paginator.num_pages)

    context = {'etatarrives': etatarrives, 'form': form}

    # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
    if arrivee.count() == 0 and form.is_valid():
        context['no_results'] = True

    return render(request, 'afficher_deplacement_arrive_admin.html', context)
