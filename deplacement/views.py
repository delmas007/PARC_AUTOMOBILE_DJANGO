from django.shortcuts import render, redirect, get_object_or_404

from Model.models import Deplacement
from deplacement.forms import DeplacementForm


# Create your views here.
def enregistrer_deplacement(request):
    if request.method == 'POST':
        form = DeplacementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('deplacement:enregistrer_deplacement')
    else:
        form = DeplacementForm()

    return render(request, 'enregistrer_deplacement.html', {'form': form})


def liste_deplacement(request):
    deplacement = Deplacement.objects.filter(depart=False, arrivee=False)
    return render(request, 'afficher_deplacement.html', {'deplacements': deplacement})


def depart(request, pk):
    deplacement = get_object_or_404(Deplacement, pk=pk)
    deplacement.depart = True
    deplacement.save()  # Ligne corrigée
    return redirect('deplacement:liste_deplacement')

def liste_deplacement_en_cours(request):
    deplacement = Deplacement.objects.filter(depart=True, arrivee=False)
    return render(request, 'afficher_deplacement.html', {'deplacements': deplacement})