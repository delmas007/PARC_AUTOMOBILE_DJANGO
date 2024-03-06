from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_GET

from entretien.forms import EntretienForm


# Create your views here.

def Ajouter_Entretien(request):
    if request.method == 'POST':
        form = EntretienForm(request.POST, request.FILES)
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


class TypeEntretien:
    pass


@require_GET
def get_type_entretien_data(request):
    # Récupérer l'ID du type d'entretien fourni dans les paramètres de la requête
    type_entretien_id = request.GET.get('type_entretien_id')

    # Vérifier si l'identifiant du type d'entretien est fourni
    if type_entretien_id is not None:
        # Récupérer le type d'entretien correspondant à l'ID spécifié
        try:
            type_entretien = TypeEntretien.objects.get(pk=type_entretien_id)
            data = {'nom': type_entretien.nom}
            return JsonResponse(data)
        except TypeEntretien.DoesNotExist:
            return JsonResponse({'error': 'Type d\'entretien non trouvé'}, status=404)
    else:
        return JsonResponse({'error': 'Identifiant du type d\'entretien non spécifié'}, status=400)