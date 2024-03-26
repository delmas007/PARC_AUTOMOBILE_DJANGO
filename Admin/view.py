import calendar

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.db.models import Sum
from django.http import HttpResponse
from xhtml2pdf import pisa

from Admin.views import rapport_carburant_mensuel
from Admin.views2 import courbe_entretien_mensuel, courbe_incident_vehicule_mensuel
from Model.models import Vehicule, Carburant, Entretien, \
    Deplacement, Incident


@login_required(login_url='Connexion')
def rapport_entretien_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
            return courbe_entretien_mensuel(request)
    else:
        vehicule = Vehicule.objects.all()
        context = {'vehicules': vehicule}
        return render(request, 'rapport_entretien_mensuel.html', context)


@login_required(login_url='Connexion')
def rapport_incident_vehicule_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_incident_vehicule_mensuel(request)
    vehicules = Vehicule.objects.all()
    context = {'vehicules': vehicules}
    return render(request, 'rapport_incident_vehicule_mensuel.html', context)


def rapport_entretien_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        voitures = Vehicule.objects.all()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            entretien = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                                 date_entretien__year=annee)

            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_entretien = entretien.count()

            html_content = f"""
                    <html>
                    <head>
                    <title>Rapport</title>
                    <style>
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                border: 1px solid black;
                                padding: 8px;
                                text-align: center;
                            }}
                            th {{
                                background-color: #f2f2f2;
                            }}
                            h1, h2 {{
                                text-align: center;
                            }}
                            .center {{
                                text-align: center;
                            }}
                    </style>
                    </head>
                    <body class="center">
                    <h1>Rapport Entretien de {mois_lettre} {annee}  de {vehicule}</h1>
                """

            if entretien:
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                 """
                for reparation in entretien:
                    html_content += f"""
                    <tr><td>{reparation.date_entretien}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                """
                html_content += f"""

                <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                 </table>
                """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            # Générer le contenu HTML du PDF
            html_content = f"""
            <html>
            <head>
            <title>Rapport PDF</title>
            <style>
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                border: 1px solid black;
                                padding: 8px;
                                text-align: center;
                            }}
                            th {{
                                background-color: #f2f2f2;
                            }}
                            h1, h2 {{
                                text-align: center;
                            }}
                            .center {{
                                text-align: center;
                            }}
            </style>
            </head>
            <body class="center">
            <h1>Rapport Entretien de {mois_lettre} {annee}</h1>
            """

            # Filtrer les incidents pour le mois et l'année spécifiés
            entretiens = Entretien.objects.filter(date_entretien__month=mois, date_entretien__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if entretiens:

                # Boucle sur chaque conducteur pour générer le rapport
                for voiture in voitures:

                    # Filtrer les incidents pour ce conducteur
                    entretiens_vehicule = entretiens.filter(vehicule=voiture)
                    html_content += f"""
                    <h2>Rapport de {voiture}</h2>
                    
                                     """

                    # Vérifier s'il y a des incidents pour ce conducteur
                    if entretiens_vehicule:
                        html_content += f"""
                                        <table border="1">
                                        <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                                        """

                        # Boucle sur chaque incident pour ce conducteur
                        for entretien in entretiens_vehicule:
                            html_content += f"""
                                                <tr><td>{entretien.date_entretien}</td><td>{entretien.type}</td><td>{entretien.prix_entretient}</td><td>{entretien.utilisateur}</td></tr>
                                            """

                            # Calculer le nombre total d'incidents pour ce conducteur
                        total_entretien = entretiens_vehicule.aggregate(Sum('prix_entretient'))[
                                              'prix_entretient__sum'] or 0
                        # Calculer les totaux pour ce conducteur
                        total_vehicule = entretiens_vehicule.filter(vehicule=entretien.vehicule).count()
                        html_content += f"""
                            <tr><td>Total</td><td>{total_vehicule}</td><td>{total_entretien}</td></tr>
                        """
                    else:
                        html_content += "<tr><td colspan='3'>Aucun entretien trouvé pour ce conducteur.</td></tr>"

                    html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            # Fermer les balises HTML
            html_content += f"""
            </body>
            </html>
            """

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Entretien de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'attachment; filename="Rapport Entretien de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def rapport_incident_vehicule_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        vehicules = Vehicule.objects.all()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            # Récupérer les données de carburant et d'entretien
            incidents = Incident.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                date_premiere__year=annee)

            html_content = f"""
                    <html>
                    <head>
                    <title>Rapport</title>
                    <style>
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                border: 1px solid black;
                                padding: 8px;
                                text-align: center;
                            }}
                            th {{
                                background-color: #f2f2f2;
                            }}
                            h1, h2 {{
                                text-align: center;
                            }}
                            .center {{
                                text-align: center;
                            }}
                    </style>
                    </head>
                    <body class="center">
                    <h1>Rapport Carburant de {mois_lettre} {annee}  de {vehicule}</h1>
                """

            if incidents:
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Conducteur</th><th>Gestionnaire</th><th>Description</th></tr>
                 """


                for incident in incidents:
                    incident_conducteur = incident.conducteur
                    if not incident.conducteur:
                        incident_conducteur =" "
                    incident_gestionnaire = incident.utilisateurs
                    if not incident.utilisateurs:
                        incident_gestionnaire =" "
                    html_content += f"""
                    <tr><td>{incident.date_premiere}</td><td>{incident_conducteur}</td><td>{incident_gestionnaire}</td><td>{incident.description_incident}</td></tr>
                """

            else:
                html_content += "<p>Aucune donnée de incident disponible.</p>"
        else:
            # Générer le contenu HTML du PDF
            html_content = f"""
            <html>
            <head>
            <title>Rapport PDF</title>
            <style>
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                border: 1px solid black;
                                padding: 8px;
                                text-align: center;
                            }}
                            th {{
                                background-color: #f2f2f2;
                            }}
                            h1, h2 {{
                                text-align: center;
                            }}
                            .center {{
                                text-align: center;
                            }}
            </style>
            </head>
            <body class="center">
            <h1>Rapport Incidents de {mois_lettre} {annee}</h1>
            """

            # Filtrer les incidents pour le mois et l'année spécifiés
            incidents = Incident.objects.filter(date_premiere__month=mois, date_premiere__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if incidents:
                # Boucle sur chaque conducteur pour générer le rapport
                for vehicule in vehicules:

                    # Filtrer les incidents pour ce conducteur
                    incidents_vehicule = incidents.filter(vehicule=vehicule)
                    html_content += f"""
                                    <h2>Rapport de {vehicule}</h2>
                                    """

                    # Vérifier s'il y a des incidents pour ce conducteur
                    if incidents_vehicule:
                        html_content += f"""
                                        <table border="1">
                                        <tr><th>Date</th><th>Conducteur</th><th>Gestionnaire</th><th>Description</th></tr>
                                         """

                        # Boucle sur chaque incident pour ce conducteur
                        for incident in incidents_vehicule:
                            incident_conducteur = incident.conducteur
                            if not incident.conducteur:
                                incident_conducteur =" "
                            incident_gestionnaire = incident.utilisateurs
                            if not incident.utilisateurs:
                                incident_gestionnaire =" "
                            html_content += f"""
                                                <tr><td>{incident.date_premiere}</td><td>{incident_conducteur}</td><td>{incident_gestionnaire}</td><td>{incident.description_incident}</td></tr>
                                            """

                            # Calculer le nombre total d'incidents pour ce conducteur
                        total_incident = incidents_vehicule.count()

                        # Calculer les totaux pour ce conducteur
                        total_vehicule = incidents_vehicule.filter(vehicule=incident.vehicule).count()
                        html_content += f"""
                            <tr><td>Total</td><td>{total_vehicule}</td><td>{total_incident}</td></tr>
                        """
                    else:
                        html_content += "<tr><td>Aucun incident trouvé pour ce vehicule.</td></tr>"

                    html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            # Fermer les balises HTML
            html_content += f"""
            </body>
            </html>
            """

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            conducteur = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Incident Véhicule de {mois_lettre} {annee}  de {conducteur}.pdf"'
        else:
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Incident Véhicule de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response

@login_required(login_url='Connexion')
def ProfilAdmin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    return render(request, 'Profil_admin.html')
