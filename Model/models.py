# models.py
import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Vous devez entrer un nom d'utilisateur")

        user = self.model(
            username=username
            # username = self.get_by_natural_key(username)
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


class Roles(models.Model):
    ADMIN = 'ADMIN'
    GESTIONNAIRE = 'GESTIONNAIRE'
    CONDUCTEUR = 'CONDUCTEUR'
    CLIENT = 'CLIENT'

    ROLE_CHOICES = [
        (ADMIN, 'ADMIN'),
        (GESTIONNAIRE, 'GESTIONNAIRE'),
        (CONDUCTEUR, 'CONDUCTEUR'),
        (CLIENT, 'CLIENT'),

    ]
    role = models.CharField(max_length=200, choices=ROLE_CHOICES)

    def __str__(self):
        return self.get_role_display()


class Conducteur(models.Model):
    nom = models.CharField(max_length=250)
    prenom = models.CharField(max_length=250, )
    numero_permis_conduire = models.CharField(max_length=20, unique=True, )
    date_embauche = models.DateField(blank=True, null=True)
    date_de_naissance = models.DateField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15, unique=True)
    adresse = models.CharField(blank=True)
    disponibilite = models.BooleanField(default=True)
    email = models.CharField(max_length=250, blank=True)
    num_cni = models.CharField(max_length=250, unique=True)
    image = models.ImageField(upload_to='ImagesConducteur/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_permis_conduire}"

    class Meta:
        ordering = ["nom"]


class Utilisateur(AbstractBaseUser):
    mon_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    username = models.CharField(
        unique=True,
        max_length=255,
        blank=False
    )
    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False
    )
    nom = models.CharField(max_length=250, verbose_name='nom')
    prenom = models.CharField(max_length=250)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    roles = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
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
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE)
    numero_immatriculation = models.CharField(max_length=250)
    couleur = models.CharField(max_length=250, blank=True, null=True)
    carte_grise = models.CharField(max_length=250)
    date_mise_circulation = models.DateField(blank=True, null=True)
    date_d_edition = models.DateField(blank=True, null=True)
    carrosserie = models.CharField(max_length=250, blank=True, null=True)
    place_assises = models.IntegerField(blank=True, null=True)
    date_expiration_assurance = models.DateField()
    date_videnge = models.DateField()
    kilometrage = models.IntegerField()
    # prix_location
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

    class Meta:
        ordering = ['numero_immatriculation']
    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # Récupère l'objet request s'il existe
        self.utilisateur = request.user if request else None  # Assigne l'utilisateur connecté ou None
        super().save(*args, **kwargs)


class Demande_prolongement(models.Model):
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    duree = models.CharField(max_length=250, )
    motif = models.CharField(max_length=250, )
    en_cours = models.BooleanField(default=True)
    accepter = models.BooleanField(default=False)
    refuser = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.conducteur.nom} {self.conducteur.prenom}"


class Deplacement(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    demande_prolongement = models.ForeignKey(Demande_prolongement, on_delete=models.SET_NULL, null=True)
    date_depart = models.DateTimeField()
    niveau_carburant = models.IntegerField()
    duree_deplacement = models.CharField(max_length=250, )
    depart = models.BooleanField(default=False)
    arrivee = models.BooleanField(default=False)
    kilometrage_depart = models.IntegerField()
    statut = models.CharField(
        max_length=50,
        choices=[
            ('en cours', 'En cours...'),
            ('arrivée', 'Arrivée')
        ],
        default='en cours'
    )

    def save(self, *args, **kwargs):
        if self.depart and not self.date_depart:
            self.date_depart = timezone.now()

        super(Deplacement, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicule} - {self.conducteur.nom}"


class Demande_location(models.Model):
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    en_cours = models.BooleanField(default=True)
    accepter = models.BooleanField(default=False)
    refuser = models.BooleanField(default=False)
    paniers = models.ManyToManyField(Vehicule)


class Location(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    demande_prolongement = models.ForeignKey(Demande_prolongement, on_delete=models.SET_NULL, null=True)
    demande_location = models.ForeignKey(Demande_location, on_delete=models.SET_NULL, null=True)
    date_depart = models.DateTimeField()
    niveau_carburant = models.IntegerField()
    duree_deplacement = models.CharField(max_length=250, )
    depart = models.BooleanField(default=False)
    arrivee = models.BooleanField(default=False)
    kilometrage_depart = models.IntegerField()
    statut = models.CharField(
        max_length=50,
        choices=[
            ('en cours', 'En cours...'),
            ('arrivée', 'Arrivée')
        ],
        default='en cours'
    )


class Carburant(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)

    type = models.CharField(
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
    prix = models.IntegerField()
    quantite = models.IntegerField()


class Entretien(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    date_entretien = models.DateField()
    prix_entretient = models.IntegerField()
    description = models.TextField(blank=True)


class EtatArrive(models.Model):
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='deplacement_etat')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='utilisateur_etat')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    kilometrage_arrive = models.IntegerField()
    niveau_carburant_a = models.IntegerField()
    date_arrive = models.DateField()

    def save(self, *args, **kwargs):
        if self.date_arrive:
            self.date_arrive = timezone.now()
        super().save(*args, **kwargs)


class Incident(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True)
    description_incident = models.TextField()


class Photo(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True)
    images = models.ImageField(upload_to='Images/', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, blank=True, null=True)
    demande_prolongement = models.ForeignKey(Demande_prolongement, on_delete=models.SET_NULL, blank=True, null=True)
    etat_arrive = models.ForeignKey(EtatArrive, on_delete=models.SET_NULL, blank=True, null=True)
    deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL, blank=True, null=True)
