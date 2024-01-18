from django.urls import path

from deplacement.views import enregistrer_deplacement, depart, liste_deplacement, liste_deplacement_en_cours, arrivee, \
    liste_deplacement_arrive

app_name = 'deplacement'

urlpatterns = [
    path('enregistrer_deplacement/', enregistrer_deplacement, name='enregistrer_deplacement'),
    path('liste_deplacement/', liste_deplacement, name='liste_deplacement'),
    path('confirmer_depart/<int:pk>/', depart, name='depart'),
    path('liste_deplacement_en_cours/', liste_deplacement_en_cours, name='liste_deplacement_en_cours'),
    path('confirmer_arrive/<int:pk>/', arrivee, name='arrivee'),
    path('liste_deplacement_arrive/', liste_deplacement_arrive, name='liste_deplacement_arrive'),

]