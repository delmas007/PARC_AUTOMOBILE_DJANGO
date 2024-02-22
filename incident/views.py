from django.shortcuts import render, redirect

from Model.models import Vehicule, Conducteur, Utilisateur
from incident.forms import IncidentForm
from django.contrib import messages

# Create your views here.


def enregistrer_incident(request):

    vehicules = Vehicule.objects.all()
    utilisateurs = Utilisateur.objects.exclude(conducteur_id__isnull=True).filter(is_active=True)

    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            messages.success(request, 'L\'incident a été enregistré avec succès.')
            return redirect('incident:enregistrer_incident')
    else:
        form = IncidentForm()

    return render(request, 'Enregistrer_incident.html', locals())


def liste_incidents_externe(request):
    return render(request, 'Liste_incidents_externe.html')


def liste_incidents_interne(request):
    return render(request, 'Liste_incidents_interne.html')

