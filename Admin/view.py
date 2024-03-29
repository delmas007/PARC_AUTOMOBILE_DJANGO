import calendar

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import formats
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
            vidange = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                               date_entretien__year=annee, type__nom="VIDANGE")
            total_vidange = vidange.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_vidange = vidange.count() or 0
            visite = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                              date_entretien__year=annee, type__nom="VISITE")
            total_visite = visite.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_visite = visite.count() or 0
            autre = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                             date_entretien__year=annee, type__nom="AUTRE")
            total_autre = autre.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_autre = autre.count() or 0
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
                    date = reparation.date_entretien
                    reparation_date = formats.date_format(date, format="l d F Y")
                    html_content += f"""
                        <tr><td>{reparation_date}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                    """
                html_content += f"""

                    <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                     </table>
                    """
                html_content += f"""
                    
                <br>
                <br>
                <br>
                    <table border=1>
                    <tr><th>Type</th><th>Nombre</th><th>Prix Total</th></tr>
                    <tr><th>Vidange</th><td>{nbre_vidange}</td><td>{total_vidange}</td></tr>
                    <tr><th>Visite</th><td>{nbre_visite}</td><td>{total_visite}</td></tr>
                    <tr><th>Autre</th><td>{nbre_autre}</td><td>{total_autre}</td></tr>
                     </table>
                    """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            # Initialiser entretiens_vehicule en dehors de la boucle
            entretiens_vehicule = None

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

                    vidange = Entretien.objects.filter(date_entretien__month=mois,
                                                       date_entretien__year=annee, type__nom="VIDANGE")
                    total_vidange = vidange.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                    nbre_vidange = vidange.count() or 0
                    visite = Entretien.objects.filter(date_entretien__month=mois,
                                                      date_entretien__year=annee, type__nom="VISITE")
                    total_visite = visite.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                    nbre_visite = visite.count() or 0
                    autre = Entretien.objects.filter(date_entretien__month=mois,
                                                     date_entretien__year=annee, type__nom="AUTRE")
                    total_autre = autre.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                    nbre_autre = autre.count() or 0
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
                            date = entretien.date_entretien
                            entretien_date = formats.date_format(date, format="l d F Y")
                            html_content += f"""
                                <tr><td>{entretien_date}</td><td>{entretien.type}</td><td>{entretien.prix_entretient}</td><td>{entretien.utilisateur}</td></tr>
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
                        html_content += "<tr><td colspan='3'>Aucun entretien trouvé pour ce vehicule.</td></tr>"

                    html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            # Utilisez entretiens_vehicule pour vérifier s'il y a eu des entretiens de véhicules
            if entretiens_vehicule:
                html_content_bas = f"""
                    <br>
                    <br>
                    <br>
                    <table border=1>
                    <tr><th>Type</th><th>Nombre</th><th>Prix Total</th></tr>
                    <tr><th>Vidange</th><td>{nbre_vidange}</td><td>{total_vidange}</td></tr>
                    <tr><th>Visite</th><td>{nbre_visite}</td><td>{total_visite}</td></tr>
                    <tr><th>Autre</th><td>{nbre_autre}</td><td>{total_autre}</td></tr>
                    </table>
                """

            # Fermer les balises HTML
            html_content += f"""
                </body>
                </html>
            """

            # Si entretiens_vehicule est défini, ajouter le tableau bas
            if entretiens_vehicule:
                html_content += html_content_bas

        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Entretien de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'inline; filename="Rapport Entretien de {mois_lettre} {annee}.pdf"'
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
            incidents_externe = Incident.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                        date_premiere__year=annee, utilisateurs__isnull=True)
            nbre_incidents_externe = incidents_externe.count()
            incidents_interne = Incident.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                        date_premiere__year=annee, conducteur__isnull=True)
            nbre_incidents_interne = incidents_interne.count()

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

                    date = incident.date_premiere
                    incident_date = formats.date_format(date, format='l d F Y')
                    incident_conducteur = incident.conducteur
                    if not incident.conducteur:
                        incident_conducteur = " "
                    incident_gestionnaire = incident.utilisateurs
                    if not incident.utilisateurs:
                        incident_gestionnaire = " "
                    html_content += f"""
                           <tr><td>{incident_date}</td><td>{incident_conducteur}</td><td>{incident_gestionnaire}</td><td>{incident.description_incident}</td></tr>
                       """
                html_content += f"""<tr><td>Total</td><td>{nbre_incidents_externe} incidents externes</td><td>{nbre_incidents_interne} incidents internes</td></tr>
                                </table>
                                   """
                if incidents_externe:
                    html_content += f"""
                                            <br>
                                            <br>
                                            <br>
                                            <table border =1>
                                            <tr><th>Conducteur</th><th>Nombre d'incidents</th></tr>
                                            """
                    conducteurs_traites = set()  # Ensemble pour garder une trace des conducteurs déjà traités

                    for incident in incidents:
                        if incident.conducteur and incident.conducteur not in conducteurs_traites:
                            incident_par_conducteur = incidents_externe.filter(conducteur=incident.conducteur).count()
                            html_content += f"""
                            
                                <tr><td>{incident.conducteur}</td><td>{incident_par_conducteur}</td></tr>
                            """
                            conducteurs_traites.add(incident.conducteur)  # Ajouter le conducteur traité à l'ensemble

                        # Créer un dictionnaire pour compter les incidents par conducteur
                    html_content += "</table>"
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
                # Créer un ensemble pour garder une trace des conducteurs déjà traités
                conducteurs_traites = set()

                # Créer un dictionnaire pour garder une trace du nombre total d'incidents par conducteur
                total_incidents_par_conducteur = {}

                # Boucle sur chaque véhicule pour générer le rapport
                for vehicule in vehicules:

                    # Filtrer les incidents pour ce véhicule
                    incidents_vehicule = incidents.filter(vehicule=vehicule)

                    html_content += f"""
                                           <h2>Rapport de {vehicule}</h2>
                                           """

                    # Vérifier s'il y a des incidents pour ce véhicule
                    if incidents_vehicule:
                        html_content += f"""
                                               <table border="1">
                                               <tr><th>Date</th><th>Conducteur</th><th>Gestionnaire</th><th>Description</th></tr>
                                                """

                        # Créer un dictionnaire pour garder une trace du nombre d'incidents par conducteur pour ce véhicule
                        incidents_par_conducteur = {}

                        # Boucle sur chaque incident pour ce véhicule
                        for incident in incidents_vehicule:
                            date = incident.date_premiere
                            incident_date = formats.date_format(date, format='l d F Y')
                            incident_conducteur = incident.conducteur if incident.conducteur else " "
                            incident_gestionnaire = incident.utilisateurs if incident.utilisateurs else " "
                            description_incident = incident.description_incident

                            # Ajouter le conducteur à la liste des conducteurs traités
                            conducteurs_traites.add(incident_conducteur)

                            # Ajouter l'incident au dictionnaire incidents_par_conducteur
                            if incident_conducteur in incidents_par_conducteur:
                                incidents_par_conducteur[incident_conducteur] += 1
                            else:
                                incidents_par_conducteur[incident_conducteur] = 1

                            html_content += f"""
                                                       <tr><td>{incident_date}</td><td>{incident_conducteur}</td><td>{incident_gestionnaire}</td><td>{description_incident}</td></tr>
                                                   """


                        # Ajouter le nombre d'incidents par conducteur au dictionnaire total_incidents_par_conducteur
                        for conducteur, nb_incidents in incidents_par_conducteur.items():
                            if conducteur in total_incidents_par_conducteur:
                                total_incidents_par_conducteur[conducteur] += nb_incidents
                            else:
                                total_incidents_par_conducteur[conducteur] = nb_incidents

                                # Calculer le nombre total d'incidents pour ce conducteur
                        incidents_interne_vehicule = incidents.filter(vehicule=vehicule, conducteur__isnull=True)
                        incidents_externe_vehicule = incidents.filter(vehicule=vehicule, utilisateurs__isnull=True)
                        total_incident = incidents_interne_vehicule.count()

                        # Calculer les totaux pour ce conducteur
                        total_vehicule = incidents_externe_vehicule.count()
                        html_content += f"""
                                                       <tr><td>Total</td><td>{total_vehicule}</td><td>{total_incident}</td></tr>
                                                   """

                    else:
                        html_content += "<tr><td>Aucun incident trouvé pour ce véhicule.</td></tr>"

                    html_content += "</table>"

                incidents_interne = incidents.filter(conducteur__isnull=True)
                incidents_externe = incidents.filter(utilisateurs__isnull=True)
                total_incidents_interne = incidents_interne.count()

                # Calculer les totaux pour ce conducteur
                total_incidents_externe = incidents_externe.count()
                html_content += f"""<br><br><br>
                <table border="1">
                <tr><th>Total incidents internes</th><th>Total incidents externe</th></tr>
                <tr><td>{total_incidents_externe} externes</td><td>{total_incidents_interne}</td></tr>
                </table>
                <br>
                <br>
                <br>
                                                                   """

                # Afficher le tableau avec le nombre total d'incidents par conducteur sur la période
                html_content += "<h2>Nombres d'incidents par conducteur sur la période :</h2>"
                html_content += "<table border='1'><tr><th>Conducteur</th><th>Nombre total d'incidents</th></tr>"

                for conducteur, nb_incidents in total_incidents_par_conducteur.items():
                    if conducteur != " ":
                        html_content += f"<tr><td>{conducteur}</td><td>{nb_incidents}</td></tr>"
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
                'Content-Disposition'] = f'inline; filename="Rapport Incident Véhicule de {mois_lettre} {annee}  de {conducteur}.pdf"'
        else:
            response[
                'Content-Disposition'] = f'inline; filename="Rapport Incident Véhicule de {mois_lettre} {annee}.pdf"'
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
