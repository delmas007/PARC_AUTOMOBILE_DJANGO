from django.shortcuts import render

from Model.models import Demande_prolongement
from Model.models import Incident


def Accueil(request):
    demande = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')[:5]
    incidents = Incident.objects.filter(conducteur__isnull=False).order_by('-date_mise_a_jour')[:5]

    demande_compte = Demande_prolongement.objects.filter(en_cours=True).order_by('-date_mise_a_jour')[:5].count()
    incidents_compte = Incident.objects.filter(conducteur__isnull=False).order_by('-date_mise_a_jour')[:5].count()
    total = demande_compte + incidents_compte
    return render(request, 'index.html', {'demandes': demande, 'incidents': incidents, 'total': total})
