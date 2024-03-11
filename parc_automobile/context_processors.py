from datetime import date, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta

from django.db.models import Subquery, Q, F
from Model.models import Demande_prolongement, EtatArrive, Incident, Deplacement, Vehicule, Photo


def accueil_data(request):
    deplacements_arrives_ids = EtatArrive.objects.values('deplacement_id')
    demande = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')
    incidents = Incident.objects.filter(conducteur__isnull=False).exclude(
        deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour')
    aujourd_hui = date.today()
    demande_compte = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour').count()
    incidents_compte = Incident.objects.filter(conducteur__isnull=False).exclude(
        deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour').count()
    # total = demande_compte + incidents_compte
    deplacement = Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui))
    nombre_deplacement = deplacement.count()
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    nombre_prolongement = Deplacement.objects.filter(id__in=prolongement_encours_ids).count()
    deplacements = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))

    nombre_deplacement_en_cours = deplacements.count()

    date_actuelle = timezone.now().date()
    une_semaine_plus_tard = date_actuelle + timedelta(days=7)
    vehicules_proches_expiration = Vehicule.objects.filter(date_expiration_assurance__lte=une_semaine_plus_tard)
    assurance_compte = Vehicule.objects.filter(date_expiration_assurance__lte=une_semaine_plus_tard).count()
    vehicules_et_jours_restants = {}

    for vehicule in vehicules_proches_expiration:
        jours_restants = (vehicule.date_expiration_assurance - date_actuelle).days
        if jours_restants < 0:
            vehicules_et_jours_restants[vehicule] = {'jours_restants': -1, 'photo': None}
        elif jours_restants == 0:
            vehicules_et_jours_restants[vehicule] = {'jours_restants': 0, 'photo': None}
        else:
            vehicules_et_jours_restants[vehicule] = {'jours_restants': jours_restants, 'photo': None}
        try:
            photo_vehicule = Photo.objects.filter(vehicule=vehicule).first()
            if photo_vehicule:
                vehicules_et_jours_restants[vehicule]['photo'] = photo_vehicule
        except ObjectDoesNotExist:
            pass

    vehicules_proches_vidanges = Vehicule.objects.filter(kilometrage__gte=F('videnge') - 100)
    vidanges_compte = Vehicule.objects.filter(kilometrage__gte=F('videnge') - 100).count()

    vehicules_proches_vidange = {}

    for vehiculee in vehicules_proches_vidanges:
        if vehiculee:
            vehicules_proches_vidange[vehiculee] = {'photo': None}
        try:
            photo_vehicule = Photo.objects.filter(vehicule=vehiculee).first()
            if photo_vehicule:
                vehicules_proches_vidange[vehiculee]['photo'] = photo_vehicule
        except ObjectDoesNotExist:
            pass


    date_actuelle = timezone.now().date()
    une_semaine_plus_tard = date_actuelle + timedelta(days=7)
    vehicules_proches_expiration_technique = Vehicule.objects.filter(date_visite_technique__lte=une_semaine_plus_tard)
    technique_compte = Vehicule.objects.filter(date_visite_technique__lte=une_semaine_plus_tard).count()
    vehicules_et_jours_restants_technique = {}

    for vehicule in vehicules_proches_expiration_technique:
        jours_restants = (vehicule.date_visite_technique - date_actuelle).days
        if jours_restants < 0:
            vehicules_et_jours_restants_technique[vehicule] = {'jours_restants': -1, 'photo': None}
        elif jours_restants == 0:
            vehicules_et_jours_restants_technique[vehicule] = {'jours_restants': 0, 'photo': None}
        else:
            vehicules_et_jours_restants_technique[vehicule] = {'jours_restants': jours_restants, 'photo': None}
        try:
            photo_vehicule = Photo.objects.filter(vehicule=vehicule).first()
            if photo_vehicule:
                vehicules_et_jours_restants_technique[vehicule]['photo'] = photo_vehicule
        except ObjectDoesNotExist:
            pass

    totals = demande_compte + incidents_compte + assurance_compte + vidanges_compte + technique_compte
    print(totals)

    return {'demandes': demande, 'inciden': incidents, 'totals': totals, 'nombre_deplacement': nombre_deplacement,
            'nombre_deplacement_en_cours': nombre_deplacement_en_cours, 'nombre_prolongement': nombre_prolongement,
            'vehicules_et_jours_restants': vehicules_et_jours_restants,
            'vehicules_et_jours_restants_technique': vehicules_et_jours_restants_technique,
            'vehicules_proches_vidange': vehicules_proches_vidange}
