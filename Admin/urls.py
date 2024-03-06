from django.urls import path

from Admin.views import inscription, employer_compte, active_emp, desactive_amp, gestionnaire_inactifs, \
    gestionnaire_a_search, gestionnaire_a_search_i, Ajouter_Carburant

app_name = 'admins'

urlpatterns = [
    path('Ajout_gestionnaire/', inscription, name='Ajout_gestionnaire'),
    path('Ajouter_Carburant/', Ajouter_Carburant, name='Ajouter_Carburant'),
    path('Compte_gestionnaire/', employer_compte, name='Compte_gestionnaire'),
    path('gestionnaire_inactifs/', gestionnaire_inactifs, name='gestionnaire_inactifs'),
    path('Active_employer/<int:employer_id>/', active_emp, name='active_emp'),
    path('recherche/', gestionnaire_a_search, name='gestionnaire_a_search'),
    path('recherche_i/', gestionnaire_a_search_i, name='gestionnaire_a_search_i'),
    path('Desactive_employer/<int:employer_id>/', desactive_amp, name='desactive_amp'),

]