from django.shortcuts import render

from gestion_cout.forms import EntretienForm


# Create your views here.

def Ajouter_Entretien(request):
    if request.method == 'POST':
        form = EntretienForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = EntretienForm()
    return render(request, 'ajouter_vehicule.html', {'form': form, 'marques': marques})