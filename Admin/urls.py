from django.urls import path

from Admin.views import inscription, employer_compte, active_emp, desactive_amp, gestionnaire_inactifs, \
    gestionnaire_a_search, gestionnaire_a_search_i, Ajouter_Carburant, liste_Carburant, \
    Carburant_search, dashboard_admins, rapport_admins, rapport_mensuel_admins, generate_pdf, create_pdf, \
    CustomPasswordResetConfirmView, ChangerMotDePasse_admin

app_name = 'admins'

urlpatterns = [
    path('dashboard_admins/', dashboard_admins, name='dashboard_admins'),
    path('Ajout_gestionnaire/', inscription, name='Ajout_gestionnaire'),
    path('Ajouter_Carburant/', Ajouter_Carburant, name='Ajouter_Carburant'),
    path('Compte_gestionnaire/', employer_compte, name='Compte_gestionnaire'),
    path('gestionnaire_inactifs/', gestionnaire_inactifs, name='gestionnaire_inactifs'),
    path('Active_employer/<int:employer_id>/', active_emp, name='active_emp'),
    path('recherche/', gestionnaire_a_search, name='gestionnaire_a_search'),
    path('recherche_i/', gestionnaire_a_search_i, name='gestionnaire_a_search_i'),
    path('Desactive_employer/<int:employer_id>/', desactive_amp, name='desactive_amp'),
    path('liste_Carburant/', liste_Carburant, name='liste_Carburant'),
    path('recherche_carburant/', Carburant_search, name='Carburant_search'),
    path('rapport_admins/', rapport_admins, name='rapport_admins'),
    path('rapport_mensuel_admins/', rapport_mensuel_admins, name='rapport_mensuel_admins'),
    path('generer-pdf/', generate_pdf, name='generer_pdf'),
    path('create-pdf/', create_pdf, name='create_pdf'),
    path('reset_password_confirm/', CustomPasswordResetConfirmView, name='password_reset_confirms'),
    path('ChangerMotDePasseConducteur', ChangerMotDePasse_admin, name='ChangerMotDePasse_admin'),

]