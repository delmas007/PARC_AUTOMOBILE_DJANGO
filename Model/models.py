# models.py
import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone

from django.db import models
from enum import Enum
from django_enum import EnumField


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Vous devez entrer un nom d'utilisateur")

        user = self.model(
            username=username
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class Role(Enum):
    ADMIN = 'admin'
    GESTIONNAIRE = 'gestionnaire'
    CONDUCTEUR = 'conducteur'
    CLIENT = 'client'


class Profile(models.Model):
    role = EnumField(Role)

    def __str__(self):
        return f"{self.role}"


class Conducteur(models.Model):
    nom = models.CharField(max_length=250)
    prenom = models.CharField(max_length=250, )
    numero_permis_conduire = models.CharField(max_length=20, unique=True, )
    date_embauche = models.DateField(blank=True, null=True)
    date_de_naissance = models.DateField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15, )
    adresse = models.TextField(blank=True, null=True)
    disponibilite = models.BooleanField(default=True)
    email = models.CharField(max_length=250, blank=True, null=True)
    num_cni = models.CharField(max_length=250, )
    image = models.ImageField(upload_to='ImagesConducteur/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_permis_conduire}"


class Utilisateur(AbstractBaseUser):
    mon_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    username = models.CharField(
        unique=True,
        max_length=255,
        blank=False
    )
    nom = models.CharField(max_length=250, verbose_name='nom')
    prenom = models.CharField(max_length=250)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    objects = MyUserManager()


class Marque(models.Model):
    marque = models.CharField(unique=True, max_length=250)

    def __str__(self):
        return self.marque


class Vehicule(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE)
    numero_immatriculation = models.CharField(max_length=250)
    couleur = models.CharField(max_length=250, blank=True, null=True)
    carte_grise = models.CharField(max_length=250)
    date_mise_circulation = models.DateField(blank=True, null=True)
    date_d_edition = models.DateField(blank=True, null=True)
    type_commercial = models.CharField(max_length=250, blank=True, null=True)
    carrosserie = models.CharField(max_length=250, blank=True, null=True)
    place_assises = models.IntegerField(blank=True, null=True)
    date_expiration_assurance = models.DateField()
    date_videnge = models.DateField()
    kilometrage = models.IntegerField()
    energie = models.CharField(
        max_length=250,
        choices=[
            ('essence', 'Essence'),
            ('diesel', 'Diesel'),
            ('electrique', 'Électrique'),
            ('hybride', 'Hybride'),
            ('hybride_rechargeable', 'Hybride Rechargeable'),
            ('gaz_naturel', 'Gaz Naturel'),
            ('hydrogene', 'Hydrogène'),
        ]
    )

    def __str__(self):
        return f"{self.numero_immatriculation}"


class Deplacement(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    date_depart = models.DateTimeField()
    lieu_depart = models.CharField(max_length=250, )
    niveau_carburant = models.IntegerField()
    lieu_arrivee = models.CharField(max_length=250, )
    duree_deplacement = models.CharField(max_length=250, )
    depart = models.BooleanField(default=False)
    arrivee = models.BooleanField(default=False)
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

        super(Deplacement, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicule} - {self.date_depart}"


class Entretien(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    date_entretien = models.DateField()
    prix_entretient = models.IntegerField()
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
    images = models.ImageField(upload_to='Images/', null=True, blank=True)
