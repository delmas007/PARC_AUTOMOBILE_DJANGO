import calendar
from datetime import date, datetime

from django.db.models import Sum
from django.shortcuts import render

from django.utils.translation import gettext as french

from Model.models import Vehicule, Carburant, Entretien, Incident, Conducteur


def courbe_depense_mensuel(request):
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        prix_carburant = Carburant.objects.filter(date_mise_a_jour__month=mois, date_mise_a_jour__year=annee)
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


def courbe_depense_global(request):
    if request.method == 'POST':
        debut = request.POST.get('date_debut_periode')
        fin = request.POST.get('date_fin_periode')
        debut_date = datetime.strptime(debut, '%Y-%m-%d').date()

        if fin:
            fin_date = datetime.strptime(fin, '%Y-%m-%d').date()
        else:
            fin_date = date.today()
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        prix_carburant = Carburant.objects.filter(date_mise_a_jour__date__range=(debut_date, fin_date))
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
                      {'labels': labels, 'data': data, 'vehicule': voiture, 'debut': debut_date, 'fin': fin_date})

    return render(request, 'rapport_depense.html')


def courbe_entretien_mensuel(request):
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        vehicles = Vehicule.objects.all()
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
            'vehicules': vehicles,
        }

        return render(request, 'rapport_entretien_mensuel.html', context)

    return render(request, 'rapport_entretien_mensuel.html')


def courbe_incident_vehicule_mensuel(request):
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        voiture = Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        nbre_incident = Incident.objects.filter(date_mise_a_jour__month=mois, date_mise_a_jour__year=annee)

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


def courbe_incident_conducteur_mensuel(request):
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = french(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        conducteurs = Conducteur.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        nbre_incident = Incident.objects.filter(conducteur__isnull=False, date_mise_a_jour__month=mois,
                                                date_mise_a_jour__year=annee)

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
