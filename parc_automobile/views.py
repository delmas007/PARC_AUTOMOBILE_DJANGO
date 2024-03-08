from django.db.models import Subquery
from django.shortcuts import render

from Model.models import Demande_prolongement, EtatArrive
from Model.models import Incident


def Accueil(request):
    deplacements_arrives_ids = EtatArrive.objects.values('deplacement_id')
    demande = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')[:5]
    incidents = Incident.objects.filter(conducteur__isnull=False).exclude(deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour')[:5]

    demande_compte = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')[:5].count()
    incidents_compte = Incident.objects.filter(conducteur__isnull=False).exclude(deplacement__in=Subquery(deplacements_arrives_ids)).order_by('-date_mise_a_jour')[:5].count()
    total = demande_compte + incidents_compte
    return render(request, 'index.html', {'demandes': demande, 'incidents': incidents, 'total': total})
