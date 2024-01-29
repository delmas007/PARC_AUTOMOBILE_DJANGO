# models.py
from django.utils import timezone

from django.db import models


class Vehicule(models.Model):
    carburant = [
        ('Essence (essence sans plomb)', 'Essence'),
        ('Diesel', 'Diesel'),
        ('GPL (Gaz de pétrole liquéfié)', 'GPL'),
        ('Électricité ', 'Électricité'),
        ('Hydrogène ', 'Hydrogène'),
    ]

    marque = models.CharField(max_length=250, blank=False)
    couleur = models.CharField(max_length=250, blank=True, null=True)
    modele = models.CharField(max_length=250, blank=False)
    numero_immatriculation = models.CharField(max_length=100, unique=True)
    date_mise_en_service = models.DateField(blank=True, null=True)
    type_carburant = models.CharField(max_length=250, choices=carburant, blank=True, null=True)
    kilometrage = models.IntegerField()
    annee_fabrication = models.DateField(blank=True, null=True)
    disponibilite = models.BooleanField(default=True)
    image = models.ImageField(upload_to='vehicule_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.marque} - {self.modele} - {self.numero_immatriculation}"


class Conducteur(models.Model):
    nom = models.CharField(max_length=250, blank=True, null=True)
    prenom = models.CharField(max_length=250, blank=True, null=True)
    date_de_naissance = models.DateField(blank=True, null=True)
    numero_permis_conduire = models.CharField(max_length=20, unique=True)
    date_embauche = models.DateField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15)
    adresse = models.TextField(blank=True, null=True)
    disponibilite = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_permis_conduire}"


class Deplacement(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    date_depart = models.DateTimeField(blank=True, null=True)
    date_arrivee = models.DateTimeField(blank=True, null=True)
    lieu_depart = models.CharField(max_length=250)
    lieu_arrivee = models.CharField(max_length=250)
    details = models.TextField(blank=True, null=True)
    depart = models.BooleanField(default=False)
    arrivee = models.BooleanField(default=False)
    prix = models.IntegerField(blank=True, null=True)
    statut = models.CharField(
        max_length=50,
        choices=[
            ('en attente de départ', 'en attente de départ'),
            ('en cours', 'En cours...'),
            ('arrivée', 'Arrivée')
        ],
        default='en attente de départ'
    )

    def save(self, *args, **kwargs):
        if self.depart and not self.date_depart:
            self.date_depart = timezone.now()

        if self.arrivee and not self.date_arrivee:
            self.date_arrivee = timezone.now()

        super(Deplacement, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicule} - {self.date_depart} to {self.date_arrivee}"


class Entretien(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    date_entretien = models.DateField(blank=True, null=True)
    type_entretien = models.CharField(max_length=100)
    cout_entretien = models.DecimalField(max_digits=10, decimal_places=2)
    details_entretien = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entretien de {self.vehicule} - {self.type_entretien}"
