from django.urls import path

from deplacement.views import enregistrer_deplacement

app_name = 'deplacement'

urlpatterns = [
    path('enregistrer_deplacement/', enregistrer_deplacement, name='enregistrer_deplacement'),
]