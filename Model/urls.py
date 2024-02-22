from django.urls import path

from Model.views import Connexion, Deconnexion

app_name = 'Model'

urlpatterns = [
    # path('Connexion/', Connexion.as_view(), name='connexion'),
    path('Deconnexion/', Deconnexion.as_view(), name='Deconnexion'),

]
