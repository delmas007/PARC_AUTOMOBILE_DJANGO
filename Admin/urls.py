from django.urls import path

from Admin.views import inscription, employer_compte, active_emp, desactive_amp

app_name = 'admins'

urlpatterns = [
    path('Ajout_gestionnaire/', inscription, name='Ajout_gestionnaire'),
    path('Compte_gestionnaire/', employer_compte, name='Compte_gestionnaire'),
    path('Active_employer/<int:employer_id>/', active_emp, name='active_emp'),
    path('Desactive_employer/<int:employer_id>/', desactive_amp, name='desactive_amp'),

]