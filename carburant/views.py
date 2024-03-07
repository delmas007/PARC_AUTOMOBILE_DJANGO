from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Model.models import Carburant
from carburant.forms import ModifierCarburantForm ,AjouterCarburantForm


# Create your views here.
def Ajouter_carburant(request):
    if request.method == 'POST':
        form = AjouterCarburantForm(request.POST)
        if form.is_valid():
            carburant = form.save(commit=False)  # Je Récupere les données du formulaire sans les sauvegarder immédiatement
            carburant.prix_total = carburant.quantite * carburant.type.prix  # Je Calculer le prix total
            carburant.save()

            messages.success(request, 'Enregistrement des coûts liés au carburant !')
            return redirect('carburant:Ajouter_carburant')
    else:
        form = AjouterCarburantForm()

    context = {
        'form': form,
    }

    return render(request, 'Ajouter_carburant.html',  context)


def liste_carburant(request):
        carburant_list = Carburant.objects.all().order_by('date_mise_a_jour')

        paginator = Paginator(carburant_list.order_by('date_mise_a_jour'), 3)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            carburant_list = paginator.page(page)
        except EmptyPage:

            carburant_list = paginator.page(paginator.num_pages())

        return render(request, 'Liste_carburant.html', {'carburants': carburant_list} )


def Modifier_carburant(request, pk):
    carburant = get_object_or_404(Carburant, pk=pk)

    if request.method == 'POST':
        form = ModifierCarburantForm(request.POST, instance=carburant)
        if form.is_valid():
            carburant = form.save(commit=False)
            carburant.prix_total = carburant.quantite * carburant.type.prix
            carburant.save()

            return redirect('carburant:Liste_carburant')
    else:
        form = ModifierCarburantForm(instance=carburant)

    context = {
        'form': form,
        'carburant': carburant,
    }

    return render(request, 'Modifier_carburant.html', context)