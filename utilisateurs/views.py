from django.shortcuts import render


# Create your views here.

def Accueil_user(request):
    return render(request, 'index_user.html')
