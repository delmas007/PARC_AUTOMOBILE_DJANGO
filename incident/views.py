from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from Model.models import Vehicule, Incident, Utilisateur, Photo
from incident.forms import IncidentFormGestionnaire
from django.contrib import messages


# Create your views here.


def enregistrer_incident(request):
    if request.method == 'POST':
        form = IncidentFormGestionnaire(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                incident = form.save(commit=False)
                incident.utilisateurs = request.user
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
    incidents_list = Incident.objects.all().order_by('vehicule__incident')
    incidents = []
    for incident in incidents_list:
        # incident.images = Photo.objects.filter(incident=incident).first()
        latest_photo = Photo.objects.filter(incident=incident).order_by('-id').first()
        incidents.append({'incident': incident, 'latest_photo': latest_photo})

    paginator = Paginator(incidents_list.order_by('date_mise_a_jour'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        incidents_list = paginator.page(page)
    except EmptyPage:

        incidents_list = paginator.page(paginator.num_pages())
    return render(request, 'Liste_incidents_interne.html', {'incidents': incidents})

# def incidents_search(request):
#     form = VehiculSearchForm(request.GET)
#     vehicules = Vehicule.objects.all()
#
#     if form.is_valid():
#         query = form.cleaned_data.get('q')
#         if query:
#             vehicules = vehicules.filter(Q(marque__marque__icontains=query) |
#                                          Q(numero_immatriculation__icontains=query))
#
#         context = {'vehicules': vehicules, 'form': form}
#         # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
#         if not vehicules.exists() and form.is_valid():
#             context['no_results'] = True
#
#     return render(request, 'afficher_vehicule.html', context)
