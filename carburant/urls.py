from django.urls import path

from carburant.views import Ajouter_carburant, liste_carburant, Modifier_carburant

app_name = 'carburant'

urlpatterns = [
    path('Ajouter_carburant/', Ajouter_carburant, name='Ajouter_carburant'),
    path('liste_carburant/', liste_carburant, name='Liste_carburant'),
    path('Modifier_carburant/<int:pk>/', Modifier_carburant, name='Modifier_carburant'),

]
