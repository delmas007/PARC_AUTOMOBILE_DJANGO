from django.shortcuts import render

from Model.models import Demande_prolongement
from Model.models import Incident


def Accueil(request):
    demande = Demande_prolongement.objects.all().filter(en_cours=True)
    incidents = Incident.objects.filter(conducteur__isnull=False)

    demande_compte = Demande_prolongement.objects.all().filter(en_cours=True).count()
    incidents_compte = Incident.objects.filter(conducteur__isnull=False).count()
    total = demande_compte + incidents_compte
    return render(request, 'index.html', {'demandes': demande, 'incidents': incidents, 'total': total})
