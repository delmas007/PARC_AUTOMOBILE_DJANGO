from datetime import date, timedelta

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, Q
from django.shortcuts import render

from Model.models import Demande_prolongement, EtatArrive, Conducteur, Vehicule, Deplacement, Utilisateur
from Model.models import Incident


def Accueil(request):
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    aujourd_hui = date.today()
    incidents_externe = Incident.objects.filter(conducteur_id__isnull=False).count()
    incidents_interne = Incident.objects.filter(conducteur_id__isnull=True).count()

    nombre_vehicules = Vehicule.objects.filter(supprimer=False).count()
    nombre_conducteurs = Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True).count()
    nombre_incidents = incidents_interne + incidents_externe
    nombre_deplacement_en_attente = Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui)).count()
    nombre_deplacement_termine = Deplacement.objects.all().count()
    nombre_deplacements_en_cours = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids)).count()

    # Récupérer les déplacements récents, par exemple, les 5 derniers
    deplacements_recents = Deplacement.objects.order_by('-date_mise_a_jour')[:5]

    deplacements_planifies = Deplacement.objects.filter(date_depart__isnull=False)

    # Récupérer les véhicules disponibles
    vehicule_disponible = Vehicule.objects.filter(disponibilite=True)
    # Configurer la pagination avec 6 véhicules par page
    paginator = Paginator(vehicule_disponible, 6)
    page = request.GET.get('page', 1)

    try:
        vehicules_page = paginator.page(page)
    except PageNotAnInteger:
        vehicules_page = paginator.page(1)
    except EmptyPage:
        vehicules_page = paginator.page(paginator.num_pages)

    context = {
        'nombre_vehicules': nombre_vehicules,
        'nombre_conducteurs': nombre_conducteurs,
        'nombre_deplacements_en_cours': nombre_deplacements_en_cours,
        'nombre_incidents': nombre_incidents,
        'nombre_deplacement_en_attente': nombre_deplacement_en_attente,
        'nombre_deplacement_termine': nombre_deplacement_termine,
        'deplacements_recents': deplacements_recents,
        'vehicule_disponible': vehicules_page,
        'deplacements_planifies': deplacements_planifies,
        'now': aujourd_hui
    }

    return render(request, 'index.html', context)
