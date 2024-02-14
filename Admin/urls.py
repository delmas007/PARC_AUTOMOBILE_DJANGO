from django.urls import path

from Admin.views import inscription

app_name = 'Admin'

urlpatterns = [
    path('AjoutGestionnaire/', inscription, name='Ajout'),

]