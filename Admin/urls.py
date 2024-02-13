from django.urls import path

from Model.views import inscription

app_name = 'Admin'

urlpatterns = [
    path('Inscription/', inscription, name='inscription'),

]