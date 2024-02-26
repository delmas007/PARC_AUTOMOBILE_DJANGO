from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Model.models import Vehicule, Photo, Marque, Type_Commerciale
from vehicule.forms import VehiculeForm, VehiculSearchForm, marqueForm, VehiculeModifierForm, typeForm
from django.views.decorators.http import require_GET
from django.core.serializers import serialize


# Create your views here.

# Dans votre vue Django
def Ajouter_vehicule(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                vehicule = form.save(commit=False)
                vehicule.utilisateur = request.user
                vehicule.save()
                for uploaded_file in images:
                    photo = Photo.objects.create(vehicule=vehicule, images=uploaded_file)

                messages.success(request, 'Le véhicule a été ajouté avec succès.')
                return redirect('vehicule:Ajouter_vehicule')
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')
        else:
            print(form.errors)
    else:
        form = VehiculeForm()

    return render(request, 'ajouter_vehicule.html', {'form': form})


def liste_vehicules(request):
    vehicules_list = Vehicule.objects.all().order_by('numero_immatriculation')

    paginator = Paginator(vehicules_list.order_by('date_mise_a_jour'), 5)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        vehicules_list = paginator.page(page)
    except EmptyPage:

        vehicules_list = paginator.page(paginator.num_pages())

    return render(request, 'afficher_vehicule.html', {'vehicules': vehicules_list})


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
    photos = Photo.objects.filter(vehicule=pk)

    if request.method == 'POST':
        form = VehiculeModifierForm(request.POST, request.FILES, instance=vehicule)
        if form.is_valid():
            if request.FILES.getlist('images'):
                # Supprimez les anciennes images du véhicule
                Photo.objects.filter(vehicule=vehicule).delete()
                # Ajoutez les nouvelles images au véhicule
                for image in request.FILES.getlist('images'):
                    Photo.objects.create(vehicule=vehicule, images=image)

            # Enregistrez le formulaire du véhicule mis à jour
            form.save()

            return redirect('vehicule:liste_vehicules')
    else:
        form = VehiculeForm(instance=vehicule, initial={
            'date_mise_circulation': vehicule.date_mise_circulation,

        })

    return render(request, 'modifier_vehicule.html', {'form': form, 'vehicule': vehicule, 'photos': photos})


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
            print(form.errors)
            return JsonResponse({'errors': errors}, status=400)
    else:
        form = marqueForm()
    return render(request, 'ajouter_vehicule.html', {'form': form})


def ajouter_type(request):
    if request.method == 'POST':
        form = typeForm(request.POST)
        if form.is_valid():
            modele = form.cleaned_data['modele']
            if Type_Commerciale.objects.filter(modele=modele).exists():
                return JsonResponse({'error': 'Ce type commercial existe déjà.'}, status=400)
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = dict(form.errors.items())
            print(form.errors)
            return JsonResponse({'errors': errors}, status=400)
    else:
        form = typeForm()
    return render(request, 'ajouter_vehicule.html', {'form': form})


def details_vehicule(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)
    image = Photo.objects.filter(vehicule=vehicule_id)
    return render(request, 'vehicule_details.html', {'vehicule': vehicule, 'image': image})


@require_GET
def get_modeles(request):
    marque_id = request.GET.get('marque_id')
    modeles = Type_Commerciale.objects.filter(marque_id=marque_id)
    serialized_modeles = serialize('json', modeles)
    return JsonResponse({'modeles': serialized_modeles})
