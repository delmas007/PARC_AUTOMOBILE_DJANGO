from django.urls import path

from vehicule.views import Ajouter_vehicule, liste_vehicules, supprimer_vehicule, modifier_vehicule, vehicules_pdf, \
    vehicule_pdf

app_name = 'vehicule'

urlpatterns = [
    path('Ajouter_vehicule/', Ajouter_vehicule, name='Ajouter_vehicule'),
    path('vehicule_pdf/<int:pk>/', vehicule_pdf, name='vehicule_pdf'),
    path('vehicules_pdf/', vehicules_pdf, name='vehicules_pdf'),
    path('liste_vehicules/', liste_vehicules, name='liste_vehicules'),
    path('supprimer_vehicule/<int:pk>/', supprimer_vehicule, name='supprimer_vehicule'),
    path('modifier_vehicule/<int:pk>/', modifier_vehicule, name='modifier_vehicule'),
]
