# models.py
from django.utils import timezone

from django.db import models


class Marque(models.Model):
    marque = models.CharField(unique=True, max_length=250)

    def __str__(self):
        return self.marque


class Vehicule(models.Model):
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE)
    numero_immatriculation = models.CharField(max_length=250)
    couleur = models.CharField(max_length=250)
    carte_grise = models.CharField(max_length=250)
    date_mise_circulation = models.DateField(blank=True, null=True)
    date_d_edition = models.DateField(blank=True, null=True)
    type_commercial = models.CharField(max_length=250)
    carrosserie = models.CharField(max_length=250, blank=True, null=True)
    energie = models.CharField(max_length=250, blank=True, null=True)
    place_assises = models.IntegerField(blank=True, null=True)
    date_expiration_assurance = models.DateField(blank=True, null=True)
    date_videnge = models.DateField(blank=True, null=True)
    kilometrage = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.numero_immatriculation}"


class Conducteur(models.Model):
    nom = models.CharField(max_length=250, blank=True, null=True)
    prenom = models.CharField(max_length=250, blank=True, null=True)
    numero_permis_conduire = models.CharField(max_length=20, unique=True)
    date_embauche = models.DateField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15)
    adresse = models.TextField(blank=True, null=True)
    disponibilite = models.BooleanField(default=True)
    email = models.CharField(max_length=250)
    permis = models.CharField(max_length=250)
    num_cni = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_permis_conduire}"


class Deplacement(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    date_depart = models.DateTimeField(blank=True, null=True)
    date_arrivee = models.DateTimeField(blank=True, null=True)
    lieu_depart = models.CharField(max_length=250)
    niveau_carburant = models.IntegerField()
    lieu_arrivee = models.CharField(max_length=250)
    duree_deplacement = models.CharField(max_length=250)
    depart = models.BooleanField(default=False)
    arrivee = models.BooleanField(default=False)
    prix = models.IntegerField(blank=True, null=True)
    kilometrage_depart = models.IntegerField()
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
    prix_entretient = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)


class EtatArrive(models.Model):
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, null=True)
    kilometrage_arrive = models.IntegerField()
    niveau_carburant_a = models.IntegerField()
    date_arrive = models.DateField()


class Incident(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    description_incident = models.TextField()


class Photo(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='Images/', null=True, blank=True)
