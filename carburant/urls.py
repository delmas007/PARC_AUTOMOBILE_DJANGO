from django.urls import path

from carburant.views import Ajouter_carburant

app_name = 'carburant'

urlpatterns = [
    path('Ajouter_carburant/', Ajouter_carburant, name='Ajouter_carburant'),

]
