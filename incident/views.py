from datetime import timedelta, date

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Model.models import Vehicule, Incident, Utilisateur, Photo
from incident.forms import IncidentFormGestionnaire, IncidentSearchForm, IncidentModifierForm
from django.contrib import messages


# Create your views here.


def enregistrer_incident(request):
    if request.method == 'POST':
        form = IncidentFormGestionnaire(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                incident = form.save(commit=False)
                #incident.utilisateurs = request.user
                incident.save()
                for uploaded_file in images:
                    photo = Photo.objects.create(incident=incident, images=uploaded_file)

                messages.success(request, 'L\'incident a été ajouté avec succès.')
                return redirect('incident:enregistrer_incident')
            else:
                form.add_error('images', 'Vous ne pouvez sélectionner que 6 images.')
    else:
        form = IncidentFormGestionnaire()

    return render(request, 'Enregistrer_incident.html', locals())


def liste_incidents_externe(request):
    return render(request, 'Liste_incidents_externe.html')


def liste_incidents_interne(request):
    aujourd_hui = date.today()

    # Calculer la date d'une semaine avant la date actuelle
    une_semaine_avant = aujourd_hui - timedelta(days=7)

    # Filtrer les incidents pour obtenir ceux qui ont été mis à jour au cours de la semaine précédente
    incidents_list = Incident.objects.filter(date_mise_a_jour__gte=une_semaine_avant)
    incidents = {}
    for item_incident in incidents_list:
        latest_photo = get_latest_photo(item_incident)
        incidents[item_incident.id] = {'incident': item_incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 3)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    return render(request, 'Liste_incidents_interne.html', {'incidents': incidents_page, 'paginator': paginator})


def get_latest_photo(incident):
    return Photo.objects.filter(incident=incident).order_by('-id').first()


def incidents_search(request):
    form = IncidentSearchForm(request.GET)
    incidents_list = Incident.objects.all()
    incidents = {}

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            incidents_list = incidents_list.filter(Q(vehicule__numero_immatriculation__icontains=query) |
                                                   Q(description_incident__icontains=query) |
                                                   Q(vehicule__marque__marque__icontains=query))
    for incident in incidents_list:
        latest_photo = get_latest_photo(incident)
        incidents[incident.id] = {'incident': incident, 'latest_photo': latest_photo}

    paginator = Paginator(list(incidents.values()), 3)

    page = request.GET.get('page')
    try:
        incidents_page = paginator.page(page)
    except PageNotAnInteger:
        incidents_page = paginator.page(1)
    except EmptyPage:
        incidents_page = paginator.page(paginator.num_pages)

    context = {'incidents': incidents_page, 'form': form, 'paginator': paginator}
    # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
    if not incidents and form.is_valid():
        context['no_results'] = True
    return render(request, 'Liste_incidents_interne.html', context)


def incident_interne_detail(request, pk):
    incident = get_object_or_404(Incident, id=pk)
    image = Photo.objects.filter(incident=incident)
    return render(request, 'incident_interne_details.html', {'incident': incident, 'image': image})


def modifier_incident_interne(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    photos = Photo.objects.filter(incident=incident)

    if request.method == 'POST':
        form = IncidentModifierForm(request.POST, request.FILES, instance=incident)
        if form.is_valid():
            form.instance.utilisateurs = request.user
            if request.FILES.getlist('images'):
                for image in request.FILES.getlist('images'):
                    Photo.objects.create(incident=incident, images=image)
            form.save()
            return redirect('incident:liste_incidents_interne')
    else:
        form = IncidentModifierForm(instance=incident)
    return render(request, 'modifier_incident_interne.html', {'form': form, 'incident': incident, 'photos': photos})