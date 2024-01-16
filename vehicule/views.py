from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import get_template
from django.urls import reverse
from xhtml2pdf import pisa

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
    numero_filter = request.GET.get('numero', None)
    modele_filter = request.GET.get('modele', None)

    if numero_filter:
        vehicules = vehicules.filter(numero_immatriculation=numero_filter)
    if modele_filter:
        vehicules = vehicules.filter(modele=modele_filter)
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



def vehicule_pdf(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_rendez_vous_{vehicule.pk}.pdf"'

    template = get_template('facture_template.html')
    html = template.render({'rendez_vous': vehicule})

    # Create a PDF file
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    return response


