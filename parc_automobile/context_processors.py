from datetime import date

from django.db.models import Subquery, Q
from Model.models import Demande_prolongement, EtatArrive, Incident, Deplacement, Vehicule


def accueil_data(request):
    deplacements_arrives_ids = EtatArrive.objects.values('deplacement_id')
    demande = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')[:5]
    incidents = Incident.objects.filter(conducteur__isnull=False).exclude(deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour')[:5]
    aujourd_hui = date.today()
    demande_compte = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')[:5].count()
    incidents_compte = Incident.objects.filter(conducteur__isnull=False).exclude(deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour')[:5].count()
    total = demande_compte + incidents_compte
    deplacement = Deplacement.objects.filter(Q(date_depart__gt=aujourd_hui))
    nombre_deplacement = deplacement.count()
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    nombre_prolongement = Deplacement.objects.filter(id__in=prolongement_encours_ids).count()
    deplacements = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))
    vehicules=Vehicule.objects.all()
    nombre_deplacement_en_cours = deplacements.count()
    return {'demandes': demande, 'incidents': incidents, 'total': total,'nombre_deplacement': nombre_deplacement, 'nombre_deplacement_en_cours': nombre_deplacement_en_cours, 'nombre_prolongement': nombre_prolongement}
