from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from Model.models import Conducteur
from .forms import ConducteurForm, ConducteurSearchForm


def ajouter_conducteur(request):
    if request.method == 'POST':
        form = ConducteurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le conducteur a été ajouté avec succès.')
            return redirect('conducteur:ajouter_conducteur')
    else:
        form = ConducteurForm()
    return render(request, 'ajouter_conducteur.html', {'form': form})


def tous_les_conducteurs(request):
    conducteurs = Conducteur.objects.all()
    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs})


def supprimer_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)
    conducteur.delete()
    return redirect('conducteur:tous_les_conducteurs')


def modifier_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, pk=conducteur_id)

    if request.method == 'POST':
        form = ConducteurForm(request.POST, instance=conducteur)
        if form.is_valid():
            form.save()
            return redirect('conducteur:tous_les_conducteurs')
    else:
        form = ConducteurForm(instance=conducteur, initial={
            'date_de_naissance': conducteur.date_de_naissance,
            'date_embauche': conducteur.date_embauche,
        })

    return render(request, 'modifier_conducteur.html', {'form': form, 'conducteur': conducteur})


def conducteur_search(request):
    form = ConducteurSearchForm(request.GET)
    conducteurs = Conducteur.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            conducteurs = conducteurs.filter(
                nom__icontains=query) | conducteurs.filter(
                prenom__icontains=query) | conducteurs.filter(
                numero_telephone__icontains=query)

    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs, 'search_form': form})


def conducteur_pdf(request, pk):
    conducteur = get_object_or_404(Conducteur, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Conducteur_{conducteur.pk}.pdf"'

    template = get_template('info_conducteur.html')
    html = template.render({'conducteur': conducteur})
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    return response
