from django.urls import path

from deplacement.views import enregistrer_deplacement, depart, liste_deplacement

app_name = 'deplacement'

urlpatterns = [
    path('enregistrer_deplacement/', enregistrer_deplacement, name='enregistrer_deplacement'),
    path('liste_deplacement/', liste_deplacement, name='liste_deplacement'),
    path('confirmer_depart/<int:pk>/', depart, name='depart'),

]