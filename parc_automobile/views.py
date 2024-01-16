from django.shortcuts import render


def Accueil(request):
    return render(request, 'index.html')
