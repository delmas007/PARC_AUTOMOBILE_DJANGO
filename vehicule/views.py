from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Model.models import Vehicule, Photo, Marque
from vehicule.forms import VehiculeForm, VehiculSearchForm, marqueForm


# Create your views here.

def Ajouter_vehicule(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.save()
            # Traitement des fichiers téléchargés
            for uploaded_file in request.FILES.getlist('images'):
                photo = Photo.objects.create(vehicule=vehicule, images=uploaded_file)
            messages.success(request, 'Le véhicule a été ajouté avec succès.')
            return redirect('vehicule:Ajouter_vehicule')
        else:
            print(form.errors)
    else:
        form = VehiculeForm()

    return render(request, 'ajouter_vehicule.html', {'form': form})


def liste_vehicules(request):
    vehicules_list = Vehicule.objects.all().order_by('numero_immatriculation')

    # Définir le nombre d'éléments par page
    items_per_page = 5
    paginator = Paginator(vehicules_list, items_per_page)

    # Récupérer le numéro de page à partir des paramètres GET
    page = request.GET.get('page')

    try:
        vehicules = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        vehicules = paginator.page(1)
    except EmptyPage:
        # Si la page est hors de portée (par exemple, 9999), afficher la dernière page
        vehicules = paginator.page(paginator.num_pages)

    return render(request, 'afficher_vehicule.html', {'vehicules': vehicules})


def vehicul_search(request):
    form = VehiculSearchForm(request.GET)
    vehicules = Vehicule.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            vehicules = vehicules.filter(Q(marque__marque__icontains=query) |
                                         Q(numero_immatriculation__icontains=query))

        context = {'vehicules': vehicules, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not vehicules.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_vehicule.html', context)


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
    return render(request, 'modifier_vehicule.html', {'form': form, 'vehicule': vehicule})


def vehicule_pdf(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    image = Photo.objects.filter(vehicule=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{vehicule.marque}_info.pdf"'

    template = get_template('info_vehicule.html')
    html = template.render({'vehicule': vehicule, 'image': image})

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

def details_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    return render(request, 'afficher_vehicule.html', {'vehiculet': vehicule})