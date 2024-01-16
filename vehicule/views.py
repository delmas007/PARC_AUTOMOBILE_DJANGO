from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from Model.models import Vehicule
from vehicule.forms import VehiculeForm, VehiculeForme


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


def liste_vehicules(request):
    vehicules = Vehicule.objects.all()
    return render(request, 'afficher_vehicule.html', {'vehicules': vehicules})


def supprimer_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    vehicule.delete()
    return redirect('vehicule:liste_vehicules')


def modifier_vehicule(request, pk):
    context = {}
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        form = VehiculeForme(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modifier avec succès !')
        else:
            context['errors'] = form.errors

    form = VehiculeForme(instance=vehicule)
    context['form'] = form
    return render(request, 'modifier_vehicule.html', context)
