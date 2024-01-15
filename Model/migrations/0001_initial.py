# Generated by Django 4.2.7 on 2024-01-15 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conducteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('ate_de_naissance', models.DateField()),
                ('numero_permis_conduire', models.CharField(max_length=20, unique=True)),
                ('date_embauche', models.DateField()),
                ('numero_telephone', models.CharField(max_length=15)),
                ('adresse', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Vehicule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marque', models.CharField(max_length=250)),
                ('modele', models.CharField(max_length=250)),
                ('numero_immatriculation', models.CharField(max_length=100, unique=True)),
                ('date_mise_en_service', models.DateField()),
                ('type_carburant', models.CharField(max_length=50)),
                ('kilometrage', models.PositiveIntegerField()),
                ('annee_fabrication', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Entretien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_entretien', models.DateField()),
                ('type_entretien', models.CharField(max_length=100)),
                ('cout_entretien', models.DecimalField(decimal_places=2, max_digits=10)),
                ('details_entretien', models.TextField()),
                ('vehicule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Model.vehicule')),
            ],
        ),
    ]
