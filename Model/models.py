# models.py

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

    def __str__(self):
        return f"{self.marque} {self.modele} - {self.numero_immatriculation}"


class Conducteur(models.Model):
    nom = models.CharField(max_length=250, blank=True, null=True)
    prenom = models.CharField(max_length=250, blank=True, null=True)
    date_de_naissance = models.DateField(blank=True, null=True)
    numero_permis_conduire = models.CharField(max_length=20, unique=True)
    date_embauche = models.DateField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_permis_conduire}"


class Entretien(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    date_entretien = models.DateField(blank=True, null=True)
    type_entretien = models.CharField(max_length=100)
    cout_entretien = models.DecimalField(max_digits=10, decimal_places=2)
    details_entretien = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entretien de {self.vehicule} - {self.type_entretien}"
