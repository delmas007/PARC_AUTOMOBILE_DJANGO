from django.shortcuts import render, redirect
from django.contrib import messages
from Model.models import Carburant, type_carburant, Vehicule
from carburant.forms import CarburantForm


# Create your views here.
def Ajouter_carburant(request):
    vehicules = Vehicule.objects.all()
    if request.method == 'POST':
        form = CarburantForm(request.POST)
        if form.is_valid():
            nom_carburant = form.cleaned_data['nom']
            prix_carburant = form.cleaned_data['prix']

            # Enregistrement des données dans la table type_carburant
            type_carburant.objects.create(nom=nom_carburant, prix=prix_carburant)

            messages.success(request, 'Les informations sur le carburant a été ajouté avec succès.')
            return redirect('carburant:Ajouter_carburant')
    else:
        form = CarburantForm()
    return render(request, 'Ajouter_carburant.html', {'form': form, 'vehicules': vehicules})



