from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Model.models import Vehicule, Entretien
from entretien.forms import EntretienForm, EntretienModifierForm
from incident.forms import IncidentSearchForm, IncidentModifierForm


# Create your views here.

def Ajouter_Entretien(request):
    if request.method == 'POST':
        form = EntretienForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.utilisateur = request.user
            if 'date_visite_technique' in request.POST:
                date_entretien = request.POST.get('date_visite_technique')
                print(date_entretien)
                if date_entretien:
                    vehicule_id = form.instance.vehicule.pk
                    vehicule = Vehicule.objects.get(pk=vehicule_id)
                    vehicule.date_visite_technique = date_entretien
                    vehicule.save()
            if 'kilometrage_videnge' in request.POST:
                kilometrage_videngee = request.POST.get('kilometrage_videnge')
                print('aaaaaaaaaa')
                if kilometrage_videngee:
                    vehicule_id = form.instance.vehicule.pk
                    vehicule = Vehicule.objects.get(pk=vehicule_id)
                    vehicule.videnge = kilometrage_videngee
                    vehicule.save()
            form.save()
            messages.success(request, "L' entretien a été ajouté avec succès.")
            return redirect('entretien:Ajouter_Entretien')
        else:
            print(form.errors)
    else:
        form = EntretienForm()
    return render(request, 'enregistrer_entretient.html', {'form': form})


def liste_Entretien(request):
    entretien_list = Entretien.objects.all().order_by('-date_mise_a_jour')

    paginator = Paginator(entretien_list.order_by('date_mise_a_jour'), 5)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        entretien = paginator.page(page)
    except EmptyPage:

        entretien = paginator.page(paginator.num_pages())

    return render(request, 'afficher_entretien.html', {'entretiens': entretien})


def entretien_search(request):
    form = IncidentSearchForm(request.GET)
    entretien = Entretien.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            entretien = entretien.filter(Q(type__nom__icontains=query) |
                                         Q(vehicule__marque__marque__icontains=query) |
                                         Q(vehicule__numero_immatriculation__icontains=query) |
                                         Q(vehicule__type_commercial__modele__icontains=query))

        context = {'entretiens': entretien, 'form': form}
        paginator = Paginator(entretien.order_by('date_mise_a_jour'), 5)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            entretienss = paginator.page(page)
        except EmptyPage:
            entretienss = paginator.page(paginator.num_pages())
        context = {'entretiens': entretienss, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not entretien.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_entretien.html', context)


def details_entretien(request, entretien_id):
    entretien = get_object_or_404(Entretien, id=entretien_id)
    return render(request, 'entretien_details.html', {'entretien': entretien})


def modifier_entretien(request, pk):
    entretien = get_object_or_404(Entretien, pk=pk)

    if request.method == 'POST':
        form = EntretienModifierForm(request.POST, request.FILES, instance=entretien)
        if form.is_valid():
            form.instance.utilisateur = request.user
            form.save()

            return redirect('entretien:liste_Entretien')
    else:
        form = EntretienModifierForm(instance=entretien, initial={
            'description': entretien.description,

        })

    return render(request, 'modifier_entretien.html', {'form': form, 'entretien': entretien, })
