# models.py

from django.db import models


class Vehicule(models.Model):
    marque = models.CharField(max_length=250)
    modele = models.CharField(max_length=250)
    numero_immatriculation = models.CharField(max_length=100, unique=True)
    date_mise_en_service = models.DateField()
    type_carburant = models.CharField(max_length=50)
    kilometrage = models.PositiveIntegerField()
    annee_fabrication = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.marque} {self.modele} - {self.numero_immatriculation}"


class Conducteur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    ate_de_naissance = models.DateField()
    numero_permis_conduire = models.CharField(max_length=20, unique=True)
    date_embauche = models.DateField()
    numero_telephone = models.CharField(max_length=15)
    adresse = models.TextField()

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_permis_conduire}"


class Entretien(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL,null=True)
    date_entretien = models.DateField()
    type_entretien = models.CharField(max_length=100)
    cout_entretien = models.DecimalField(max_digits=10, decimal_places=2)
    details_entretien = models.TextField()

    def __str__(self):
        return f"Entretien de {self.vehicule} - {self.type_entretien}"
