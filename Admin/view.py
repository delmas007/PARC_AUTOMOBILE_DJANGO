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
                 <tr><th>Date</th><th>Type</th><th>Prix</th></tr>
                 """
                for reparation in entretien:
                    html_content += f"""
                    <tr><td>{reparation.date_mise_a_jour.date()}</td><td>{reparation.prix_entretient}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                """
                html_content += f"""

                <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                 </table>
                """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            html_content = f"""
            <html>
            <head><title>Rapport PDF</title></head>
            <body>
            <h1>Rapport Carburant de {mois_lettre} {annee}</h1>

            """
            carburant = Entretien.objects.filter(date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)

            for voiture in voitures:

                if carburant:
                    html_content += f"""
                           <h1>Rapport  de {voiture}</h1>
                             <table border="1">
                             <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                         """

                    for essence in carburant:
                        if voiture == essence.vehicule:
                         nbre_entretien = carburant.filter(vehicule=voiture).count()
                         print(nbre_entretien)

                             # Calculer les totaux de carburant et d'entretien
                         total_carburant = carburant.filter(vehicule=voiture).aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0

                         html_content += f"""
                                    <tr><td>{essence.date_mise_a_jour.date()}</td><td>{essence.type}</td><td>{essence.prix_entretient}</td><td>{essence.utilisateur}</td></tr>
                                """
                    html_content += f"""

                                <tr><td>Total</td><td></td><td>{nbre_entretien}</td></tr>
                                 </table>
                                """
                else:
                    html_content += "<p>Aucune donnée de carburant disponible.</p>"

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
