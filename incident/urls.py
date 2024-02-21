from django.urls import path
from incident.views import enregistrer_incident, liste_incidents_externe, liste_incidents_interne

app_name = 'incident'

urlpatterns = [
    path('enregistrer_incident/', enregistrer_incident, name='enregistrer_incident'),
    path('liste_incidents_externe/', liste_incidents_externe, name='liste_incidents_externe'),
    path('liste_incidents_interne/', liste_incidents_interne, name='liste_incidents_interne'),
]
