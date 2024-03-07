from django.shortcuts import render

from Model.models import Demande_prolongement


def Accueil(request):
    demande = Demande_prolongement.objects.all().filter(en_cours=True)
    return render(request, 'index.html',{'demande' : demande})



