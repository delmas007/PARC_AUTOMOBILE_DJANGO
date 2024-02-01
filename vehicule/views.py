from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa

from Model.models import Vehicule, Photo, Marque
from vehicule.forms import VehiculeForm, VehiculSearchForm, marqueForm


# Create your views here.

def Ajouter_vehicule(request):
    context = {}

    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            # Enregistrez d'abord le véhicule sans l'image
            vehicule = form.save()

            # Traitez chaque fichier téléchargé et associez-le au véhicule
            for uploaded_file in request.FILES.getlist('image'):
                photo = Photo.objects.create(vehicule=vehicule, image=uploaded_file)

            messages.success(request, 'Véhicule ajouté avec succès !')
            context['success'] = True
        else:
            messages.error(request, 'Erreur de modification')
            context['form_errors'] = form.errors
            print(form.errors)

    form = VehiculeForm()
    context['form'] = form
    return render(request, 'ajouter_vehicule.html', context=context)


def liste_vehicules(request):
    vehicules = Vehicule.objects.all()
    return render(request, 'afficher_vehicule.html', {'vehicules': vehicules})


def vehicul_search(request):
    form = VehiculSearchForm(request.GET)
    vehicules = Vehicule.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            vehicules = vehicules.filter(
                Q(marque__icontains=query) |
                Q(numero_immatriculation__icontains=query)
            )

    return render(request, 'afficher_vehicule.html', {'vehicules': vehicules, 'form': form})


def supprimer_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    vehicule.delete()
    return redirect('vehicule:liste_vehicules')


def modifier_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)

    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES, instance=vehicule)
        if form.is_valid():
            form.save()
            return redirect('vehicule:liste_vehicules')
    else:
        form = VehiculeForm(instance=vehicule, initial={
            'date_mise_circulation': vehicule.date_mise_circulation,
            'date_d_edition': vehicule.date_d_edition,
        })
    return render(request, 'modifier_vehicule.html', {'form': form})


def vehicule_pdf(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_rendez_vous_{vehicule.pk}.pdf"'

    template = get_template('info_vehicule.html')
    html = template.render({'vehicule': vehicule})

    # Create a PDF file
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    return response


def ajouter_marque(request):
    if request.method == 'POST':
        form = marqueForm(request.POST)
        if form.is_valid():
            marque = form.cleaned_data['marque']
            if Marque.objects.filter(marque=marque).exists():
                return JsonResponse({'error': 'Cette marque existe déjà.'}, status=400)
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'errors': errors}, status=400)
    else:
        form = marqueForm()
    return render(request, 'ajouter_vehicule.html', {'form': form})
