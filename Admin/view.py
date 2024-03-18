import calendar

from django.shortcuts import render
from django.utils.translation import gettext as _
from django.db.models import Sum
from django.http import HttpResponse
from xhtml2pdf import pisa
from Model.models import Vehicule, Carburant, Entretien, \
    Deplacement


def rapport_entretien_mensuel_admins(request):
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_entretien_mensuel.html', context)


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
            entretien = Entretien.objects.filter(vehicule=vehicule_id, date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)

            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            nbre_entretien = entretien.count()
            html_content = f"""
                    <html>
                    <head><title>Rapport</title></head>
                    <body>
                    <h1>Rapport Entretien de {mois_lettre} {annee}  de {vehicule}</h1>
                """

            if entretien:
                html_content += "<h2>Entretien</h2>"
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                 """
                for reparation in entretien:
                    html_content += f"""
                    <tr><td>{reparation.date_entretien}</td><td>{reparation.prix_entretient}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
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
            <head><title>Rapport PDF</title></head>
            <body>
            <h1>Rapport Entretien de {mois_lettre} {annee}</h1>
            """

            # Filtrer les incidents pour le mois et l'année spécifiés
            entretiens = Entretien.objects.filter(date_mise_a_jour__month=mois, date_mise_a_jour__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if entretiens:
                # Boucle sur chaque conducteur pour générer le rapport
                for voiture in voitures:

                    # Filtrer les incidents pour ce conducteur
                    entretiens_vehicule = entretiens.filter(vehicule=voiture)
                    html_content += f"""
                    <h2>Rapport de {voiture}</h2>
                    <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                                                              """

                    # Vérifier s'il y a des incidents pour ce conducteur
                    if entretiens_vehicule:

                        # Boucle sur chaque incident pour ce conducteur
                        for entretien in entretiens_vehicule:
                            html_content += f"""
                                                <table border="1">
                                                <tr><td>{entretien.date_entretien}</td><td>{entretien.vehicule}</td><td>{entretien.description_incident}</td></tr>
                                            """

                            # Calculer le nombre total d'incidents pour ce conducteur
                        total_incident = entretiens_vehicule.count()
                        # Calculer les totaux pour ce conducteur
                        total_carburant = entretiens_vehicule.filter(vehicule=entretien.vehicule).count()
                        html_content += f"""
                            <tr><td>Total</td><td>{total_carburant}</td><td>{total_incident}</td></tr>
                        """
                    else:
                        html_content += "<tr><td colspan='3'>Aucun incident trouvé pour ce conducteur.</td></tr>"

                    html_content += "</table>"

            else:
                html_content += "<p>Aucun incident trouvé pour ce mois et cette année.</p>"

            # Fermer les balises HTML
            html_content += """
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
