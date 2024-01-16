from django.shortcuts import render, redirect, get_object_or_404
from Model.models import Conducteur
from .forms import ConducteurForm


def ajouter_conducteur(request):
    if request.method == 'POST':
        form = ConducteurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('conducteur:ajouter_conducteur')
    else:
        form = ConducteurForm()
    return render(request, 'ajouter_conducteur.html', {'form': form})


def tous_les_conducteurs(request):
    conducteurs = Conducteur.objects.all()
    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs})


def supprimer_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)
    conducteur.delete()
    return redirect('conducteur:tous_les_conducteurs')
