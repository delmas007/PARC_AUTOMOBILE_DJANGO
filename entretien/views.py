from django.shortcuts import render, redirect
from django.contrib import messages
from entretien.forms import EntretienForm


# Create your views here.

def Ajouter_Entretien(request):
    if request.method == 'POST':
        form = EntretienForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le véhicule a été ajouté avec succès.')
            return redirect('vehicule:Ajouter_vehicule')
        else:
            print(form.errors)
    else:
        form = EntretienForm()
    return render(request, 'enregistrer_deplacement.html', {'form': form})