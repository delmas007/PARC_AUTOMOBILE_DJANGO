from django.urls import path

from vehicule.views import Ajouter_vehicule

app_name = 'vehicule'

urlpatterns = [
    path('Ajouter_vehicule/', Ajouter_vehicule, name='Ajouter_vehicule'),
]
