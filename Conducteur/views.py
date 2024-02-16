from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Model.models import Conducteur
from .forms import ConducteurForm, ConducteurSearchForm


def ajouter_conducteur(request):
    if request.method == 'POST':
        form = ConducteurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le conducteur a été ajouté avec succès.')
            return redirect('conducteur:ajouter_conducteur')
        else:
            print(form.errors)
    else:
        form = ConducteurForm()

    return render(request, 'ajouter_conducteur.html', {'form': form})


def tous_les_conducteurs(request):
    conducteurs = Conducteur.objects.all().order_by('nom')

    items_per_page = 5
    paginator = Paginator(conducteurs, items_per_page)
    page = request.GET.get('page')

    try:
        conducteurs = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, afficher la première page
        conducteurs = paginator.page(1)
    except EmptyPage:
        # Si la page est hors de portée (par exemple, 9999), afficher la dernière page
        conducteurs = paginator.page(paginator.num_pages)

    return render(request, 'tous_les_conducteurs.html', {'conducteurs': conducteurs})


def supprimer_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, id=conducteur_id)
    conducteur.delete()
    return redirect('conducteur:tous_les_conducteurs')


def modifier_conducteur(request, conducteur_id):
    conducteur = get_object_or_404(Conducteur, pk=conducteur_id)
    if request.method == 'POST':
        form = ConducteurForm(request.POST, request.FILES, instance=conducteur)
        if form.is_valid():
            conducteur = form.save(commit=False)
            nouveau_fichier = request.FILES.get('image', None)
            if nouveau_fichier:
                conducteur.image = nouveau_fichier
            conducteur.save()
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
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(numero_telephone__icontains=query)
            )

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
