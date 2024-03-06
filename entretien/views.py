from django.shortcuts import render, redirect
from django.contrib import messages
from entretien.forms import EntretienForm


# Create your views here.

def Ajouter_Entretien(request):
    if request.method == 'POST':
        form = EntretienForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.utilisateur = request.user
            form.save()
            messages.success(request, "L' entretien a été ajouté avec succès.")
            return redirect('entretien:Ajouter_Entretien')
        else:
            print(form.errors)
    else:
        form = EntretienForm()
    return render(request, 'enregistrer_entretient.html', {'form': form})
