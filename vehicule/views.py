from django.shortcuts import render
from django.contrib import messages
from vehicule.forms import VehiculeForm


# Create your views here.

def Ajouter_vehicule(request):
    context = {}
    if request.method == 'POST':
        # Associez l'utilisateur connecté à la partie employer du formulaire
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicule ajouté avec succès !')
        else:
            context['errors'] = form.errors

    form = VehiculeForm()
    context['form'] = form
    return render(request, 'ajouter_vehicule.html', context=context)
