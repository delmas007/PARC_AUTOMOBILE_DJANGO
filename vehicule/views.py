from django.shortcuts import render


# Create your views here.

def Ajouter_vehicule(request):
    return render(request, 'ajouter_vehicule.html')
