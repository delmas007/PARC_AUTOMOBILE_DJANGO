from datetime import datetime, timedelta
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from Model.models import Vehicule, Utilisateur, Marque, Type_Commerciale, type_carburant


class Command(BaseCommand):
    help = 'Ajoute 20 véhicules à la base de données'

    def handle(self, *args, **kwargs):
        marques = Marque.objects.all()
        types_commerciales = Type_Commerciale.objects.all()
        utilisateurs = Utilisateur.objects.all()
        carburants = type_carburant.objects.all()

        for i in range(20):
            # Générer les valeurs aléatoires
            marque = random.choice(marques)
            type_commercial = random.choice(types_commerciales)
            utilisateur = random.choice(utilisateurs)
            carburant = random.choice(carburants)

            date_mise_circulation = timezone.now() - timedelta(days=random.randint(365, 10000))
            date_expiration_assurance = date_mise_circulation + timedelta(days=random.randint(30, 365))
            date_visite_technique = date_mise_circulation + timedelta(days=random.randint(30, 365))
            kilometrage = random.randint(0, 300000)
            place_assises = random.randint(1, 7)
            taille_reservoir = random.randint(40, 80)
            videnge = random.randint(5000, 15000)

            # Créer un nouvel objet Vehicule
            vehicule = Vehicule(
                marque=marque,
                numero_immatriculation=f"IMM{i:04}",
                type_commercial=type_commercial,
                numero_chassis=f"CHAS{i:04}",
                couleur=random.choice(["Noir", "Blanc", "Rouge", "Bleu", "Vert"]),
                carte_grise=f"CG{i:04}",
                date_mise_circulation=date_mise_circulation,
                carrosserie=random.choice(["Berline", "SUV", "Coupé", "Break"]),
                place_assises=place_assises,
                date_expiration_assurance=date_expiration_assurance,
                kilometrage=kilometrage,
                image_recto=None,  # Vous pouvez ajouter des images si vous le souhaitez
                image_verso=None,  # Vous pouvez ajouter des images si vous le souhaitez
                date_visite_technique=date_visite_technique,
                taille_reservoir=taille_reservoir,
                videnge=videnge,
                energie=carburant,
                disponibilite=random.choice([True, False]),
                supprimer=False,
                utilisateur=utilisateur
            )

            # Sauvegarder l'objet dans la base de données
            vehicule.save()

        self.stdout.write(self.style.SUCCESS('20 véhicules ajoutés avec succès'))
