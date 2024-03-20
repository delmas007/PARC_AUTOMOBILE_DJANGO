import calendar
import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.translation import gettext as _
from datetime import date, datetime

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, ExpressionWrapper, fields, F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from xhtml2pdf import pisa

from Admin.forms import typeCarburantForm, CarburantSearchForm, UserRegistrationForm
from Model.models import Roles, Utilisateur, type_carburant, periode_carburant, Vehicule, Carburant, Entretien, \
    Deplacement, Conducteur, Incident, EtatArrive
from utilisateurs.forms import ChangerMotDePasse
from vehicule.forms import VehiculSearchForm
from secrets import compare_digest
from django.http import JsonResponse




@csrf_protect
def inscription(request):
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            client_role = Roles.objects.get(role=Roles.GESTIONNAIRE)
            user.roles = client_role
            user.save()
            # Récupérez l'URL de l'image téléchargée
            image_url = user.image.url if user.image else None
            # Ajoutez l'URL de l'image au contexte
            context['user_image_url'] = image_url
            return redirect('admins:Compte_gestionnaire')
        else:
            context['form'] = form
            return render(request, 'ajouter_gestionnaire.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'ajouter_gestionnaire.html', context=context)


# @login_required
def employer_compte(request):
    gestionnaires = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=True)

    return render(request, 'tous_les_gestionnaires.html', {'gestionnaires': gestionnaires})


def gestionnaire_inactifs(request):
    gestionnaires2 = Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=False)
    return render(request, 'tous_les_gestionnairess.html', {'gestionnaires2': gestionnaires2})


# @login_required
def active_emp(request, employer_id):
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()
    return redirect('admins:gestionnaire_inactifs')


def desactive_amp(request, employer_id):
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_gestionnaire')


def gestionnaire_a_search(request):
    form = VehiculSearchForm(request.GET)
    gestionnaire = Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=False)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        context = {'gestionnaires': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnaires.html', context)


def gestionnaire_a_search_i(request):
    form = VehiculSearchForm(request.GET)
    gestionnaire = Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=True)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        context = {'gestionnaires2': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnairess.html', context)


def Ajouter_Carburant(request):
    if request.method == 'POST':
        form = typeCarburantForm(request.POST)
        print(request.POST.get("nom"))
        carburant_id = request.POST.get("nom")
        carburant_prix = request.POST.get("prix")
        aujourdhui = date.today()
        if form.is_valid():

            carburant = type_carburant.objects.get(id=carburant_id)
            carburant.prix = carburant_prix
            carburant.save()
            dernier_periode = periode_carburant.objects.filter(carburant=carburant).order_by('-date_debut').first()
            if dernier_periode:

                periode = periode_carburant.objects.create(carburant=carburant, date_debut=carburant.date_mise_a_jour,
                                                           prix=carburant.prix)
                date_fin = carburant.date_mise_a_jour
                dernier_periode.date_fin = date_fin
                dernier_periode.save()
                periode.save()
            else:
                periode = periode_carburant.objects.create(carburant=carburant, date_debut=carburant.date_mise_a_jour,
                                                           prix=carburant.prix)
                periode.save()
            messages.success(request, "Carburant ajouté avec succès.")
            return redirect('admins:Ajouter_Carburant')
        else:
            print(form.errors)
    else:
        form = typeCarburantForm()
    return render(request, 'enregistrer_carburant.html', {'form': form})


def liste_Carburant(request):
    carburant_list = (
        type_carburant.objects.all()
        .annotate(hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField()))
        .order_by('-hour')
    )

    paginator = Paginator(carburant_list, 5)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        carburants = paginator.page(page)
    except EmptyPage:

        carburants = paginator.page(paginator.num_pages())

    return render(request, 'afficher_carburant.html', {'carburants': carburants})


def Carburant_search(request):
    form = CarburantSearchForm(request.GET)
    carburant = type_carburant.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            carburant = carburant.filter(Q(nom__icontains=query))

        context = {'carburants': carburant, 'form': form}
        paginator = Paginator(carburant.order_by('-date_mise_a_jour'), 5)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            carburants = paginator.page(page)
        except EmptyPage:
            carburants = paginator.page(paginator.num_pages())
        context = {'carburants': carburants, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not carburant.exists() and form.is_valid():
            context['no_results'] = True

    return render(request, 'afficher_carburant.html', context)


def dashboard_admins(request):
    vehicles = Vehicule.objects.all()
    labels = [f"{vehicle.marque} {vehicle.type_commercial}" for vehicle in vehicles]
    fuel_data = [vehicle.total_carburant_consomme() for vehicle in vehicles]
    quantites = [data['quantite'] for data in fuel_data]
    prix = [data['prix'] for data in fuel_data]

    context = {
        'labels': labels,
        'quantites': quantites,
        'prix': prix,
    }

    return render(request, 'dashoard_admins.html', context)



def rapport_depense_admins(request):
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_depense.html', context)


def rapport_depense_mensuel_admins(request):
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_depense_mensuel.html', context)


def rapport_carburant_mensuel_admins(request):
    if request.method == 'POST':
        return rapport_carburant_mensuel(request)
    else:
        vehicules = Vehicule.objects.all()
        context = {'vehicules': vehicules}
        return render(request, 'rapport_carburant_mensuel.html', context)


def rapport_incident_conducteur_mensuel_admins(request):
    conducteurs = Conducteur.objects.all()
    context = {'conducteurs': conducteurs}
    return render(request, 'rapport_incident_conducteur_mensuel.html', context)


def rapport_depense_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        voitures = Vehicule.objects.all()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            # Récupérer les données de carburant et d'entretien
            carburant = Carburant.objects.filter(vehicule=vehicule_id, date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)
            entretien = Entretien.objects.filter(vehicule=vehicule_id, date_entretien__month=mois,
                                                 date_entretien__year=annee)

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
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
                    <h1>Rapport Depense de {mois_lettre} {annee}  de {vehicule}</h1>
                """

            if carburant:
                html_content += "<h2>Carburant</h2>"
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                 """
                for essence in carburant:
                    html_content += f"""
                    <tr><td>{essence.date_mise_a_jour.date()}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                """
                html_content += f"""

                <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                 </table>
                """
            else:
                html_content += "<p>Aucune donnée de carburant disponible.</p>"
            if entretien:
                html_content += "<h2>Entretien</h2>"
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                 """
                for reparation in entretien:
                    html_content += f"""
                    <tr><td>{reparation.date_mise_a_jour.date()}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                """
                html_content += f"""

                <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                 </table>
                """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            carburant = Carburant.objects.filter(date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)
            entretien = Entretien.objects.filter(date_entretien__month=mois,
                                                 date_entretien__year=annee)
            nbre_deplacements = 0
            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
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
            <h1>Rapport Depense de {mois_lettre} {annee}</h1>
            <table border="1">
            <tr><th>Voitures</th><th>Nombre de déplacements</th><th>Quantitié</th><th>Carburant</th><th>Entretien</th><th>Total</th></tr>

            """
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture, date_mise_a_jour__month=mois,
                                                     date_mise_a_jour__year=annee)
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                carburant_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture, date_entretien__month=mois,
                                                     date_entretien__year=annee)
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                vehicule_max_carburant_id = Carburant.objects.values('vehicule').annotate(
                    total_carburant=Sum('prix_total')).order_by('-total_carburant').first()
                vehicule_max_entretien_id = Entretien.objects.values('vehicule').annotate(
                    total_entretien=Sum('prix_entretient')).order_by('-total_entretien').first()
                deplacement = Deplacement.objects.filter(vehicule=voiture,date_depart__month=mois,date_depart__year=annee).count()
                nbre_deplacements +=deplacement
                if vehicule_max_carburant_id:
                    vehicule_max_carburant = Vehicule.objects.get(id=vehicule_max_carburant_id['vehicule'])
                else:
                    vehicule_max_carburant = "Aucun donné carburant"
                if vehicule_max_entretien_id:
                    vehicule_max_entretien = Vehicule.objects.get(id=vehicule_max_entretien_id['vehicule'])
                else:
                    vehicule_max_entretien = "Aucun donné entretien"
                html_content += f"<tr> <td> {voiture} </td><td> {deplacement} </td><td> {carburant_quantite} </td><td>{carburant_vehicule}</td><td>{entretien_vehicule}</td><td>{carburant_vehicule + entretien_vehicule}</td></tr>"

            html_content += f"""
            <tr><td>Total</td><td>{nbre_deplacements}</td><td>{total_quantite}</td><td>{total_carburant}</td><td>{total_entretien}</td><td>{total_carburant + total_entretien}</td></tr>
            </table>
              <h1> plus grosse depense en carburant: {vehicule_max_carburant}<h1>
              <h1>plus grosse depense en entretien:{vehicule_max_entretien}<h1>
            </body>
            
            </html>
            """
        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Depense de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'attachment; filename="Rapport Depenses de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def rapport_depense_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        debut = request.POST.get('date_debut_periode')
        fin = request.POST.get('date_fin_periode')
        voitures = Vehicule.objects.all()
        debut_date = datetime.strptime(debut, '%Y-%m-%d').date()

        if fin:
            fin_date = datetime.strptime(fin, '%Y-%m-%d').date()
        else:
            fin_date = date.today()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            carburants = Carburant.objects.filter(vehicule=vehicule, date_mise_a_jour__date__range=(debut_date, fin_date))
            entretiens = Entretien.objects.filter(vehicule=vehicule, date_entretien__range=(debut_date, fin_date))
            total_carburant = carburants.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretiens.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburants.aggregate(Sum('quantite'))['quantite__sum'] or 0
            nbre_entretien = entretiens.count()
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
                               <h1>Rapport Depense de {debut_date} à {fin_date}  de {vehicule}</h1>
                           """

            if carburants:
                html_content += "<h2>Carburant</h2>"
                html_content += """
                            <table border="1">
                            <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                            """
                for essence in carburants:
                    html_content += f"""
                               <tr><td>{essence.date_mise_a_jour.date()}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                           """
                html_content += f"""

                           <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                            </table>
                           """
            else:
                html_content += "<p>Aucune donnée de carburant disponible.</p>"

            if entretiens:
                html_content += "<h2>Entretien</h2>"
                html_content += """
                            <table border="1">
                            <tr><th>Date</th><th>Type</th><th>Prix</th><th>Gestionnaire</th></tr>
                            """
                for reparation in entretiens:
                    html_content += f"""
                               <tr><td>{reparation.date_mise_a_jour.date()}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                           """
                html_content += f"""

                           <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                            </table>
                           """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            carburant = Carburant.objects.filter(date_mise_a_jour__date__range=(debut_date, fin_date))
            entretien = Entretien.objects.filter(date_entretien__range=(debut_date, fin_date))
            nbre_deplacements = 0
            nbres_entretien = 0
            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
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
                  <h1>Rapport Depense de {debut_date} à {fin_date}</h1> <table border="1"> 
                  <tr><th>Voitures</th><th>Nombre de deplacements</th><th>Quantitié</th><th>Carburant</th><th>Nombre 
                  entretien</th><th>Entretien</th><th>Total</th></tr>

                   """
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture,
                                                     date_mise_a_jour__date__range=(debut_date, fin_date))
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                carburant_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture,
                                                     date_entretien__range=(debut_date, fin_date))
                nbre_entretien = entretien.count()
                nbres_entretien += nbre_entretien
                vehicule_max_carburant_id = Carburant.objects.filter(
                    date_mise_a_jour__date__range=(debut_date, fin_date)).values('vehicule').annotate(
                    total_carburant=Sum('prix_total')).order_by('-total_carburant').first()
                if vehicule_max_carburant_id:
                    vehicule_max_carburant = Vehicule.objects.get(id=vehicule_max_carburant_id['vehicule'])
                else:
                    vehicule_max_carburant = "Aucun donné carburant"

                vehicule_max_entretien_id = Entretien.objects.filter(
                    date_entretien__range=(debut_date, fin_date)).values('vehicule').annotate(
                    total_entretien=Sum('prix_entretient')).order_by('-total_entretien').first()
                if vehicule_max_entretien_id:
                    vehicule_max_entretien = Vehicule.objects.get(id=vehicule_max_entretien_id['vehicule'])
                else:
                    vehicule_max_entretien = "Aucun donné entretien"

                deplacement = Deplacement.objects.filter(vehicule=voiture, date_depart__range=(debut_date,fin_date)).count()
                nbre_deplacements += deplacement
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                html_content += f"""<tr> <td> {voiture} </td><td> {deplacement} </td><td> {carburant_quantite} </td><td>{carburant_vehicule}</td><td>{nbre_entretien}</td><td>{entretien_vehicule}</td><td>{carburant_vehicule + entretien_vehicule}</td></tr>"""

            html_content += f"""
                   <tr><td>Total</td><td>{nbre_deplacements}</td><td>{total_quantite}</td><td>{total_carburant}</td><td>{nbres_entretien}</td><td>{total_entretien}</td><td>{total_carburant + total_entretien}</td></tr>
                   </table>
                   <h1> plus grosse depense en carburant: {vehicule_max_carburant}<h1>
                   <h1>plus grosse depense en entretien:{vehicule_max_entretien}<h1>
                   </body>
                   </html>
                   """
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Depense de {debut_date} à {fin_date}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'attachment; filename="Rapport Depense de {debut_date} à {fin_date}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def CustomPasswordResetConfirmView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        passe = request.POST.get('new_password')
        passe2 = request.POST.get('new_password2')

        try:
            # Rechercher l'utilisateur par nom d'utilisateur
            user = Utilisateur.objects.get(username=username)
        except Utilisateur.DoesNotExist:
            user = None
        if not user:
            messages.error(request, "L'utilisateur n'existe pas")
            return redirect('admins:password_reset_confirms')
        if passe == passe2:
            new_password = passe
            user.set_password(new_password)
            user.save()
            messages.success(request, "Mot de passe réinitialisé avec succès.")
        else:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        update_session_auth_hash(request, user)

        return redirect('admins:password_reset_confirms')
    else:
        return render(request, 'reinitialiser.html')


def ChangerMotDePasse_admin(request):
    if request.method == 'POST':
        form = ChangerMotDePasse(request.user, request.POST)
        if request.user.check_password(request.POST.get('passe')):
            if form.is_valid():
                form.save()
                messages.success(request, "Votre mot de passe a été changer.")
                return redirect('Connexion')
            else:
                messages.error(request, "Les deux mots de passe ne correspondent pas")
        else:
            messages.error(request, "Le mot de passe actuel est incorrect.")
    form = ChangerMotDePasse(request.user)
    return render(request, 'changerMotDePasse_admin.html', {'form': form})


def rapport_carburant_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        vehicule_id = request.POST.get('vehicule')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        voitures = Vehicule.objects.all()
        if vehicule_id:

            carburant = Carburant.objects.filter(vehicule=vehicule_id, date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)


            vehicule = Vehicule.objects.get(id=vehicule_id)


            deplacement = Deplacement.objects.filter(vehicule=vehicule, date_depart__month=mois,
                                                     date_depart__year=annee).order_by('date_depart')
            if deplacement:
                deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)



                deplacement_first = deplacement.first()

                deplacement_last = deplacement.filter(id__in=deplacements_etat_arrive_ids).last()
                if deplacement_last:
                    arrive = EtatArrive.objects.filter(deplacement=deplacement_last.id, date_arrive__month=mois,
                                                       date_arrive__year=annee).last()


                    total_kilometrage=arrive.kilometrage_arrive-deplacement_first.kilometrage_depart

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0

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

            if carburant:
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                 """
                for essence in carburant:
                    html_content += f"""
                    <tr><td>{essence.date_mise_a_jour.date()}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                """
                if deplacement:
                    if deplacement_last:
                        html_content += f"""
                        
                        <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                         <tr> <td colspan="4"><h2>KILOMETRAGE DU VEHICULE:{total_kilometrage}</h2></tr>
                         </table>
                        """
                    else:
                        html_content += f"""
                        <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                         <tr> <td colspan="4"><h2>Deplacement en cours</h2></tr>
                         </table>
                        """
                else:
                        html_content += f"""
                        <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                         <tr> <td colspan="4"><h2>Aucun déplacement effectué</h2></tr>
                         </table>
                        """

            else:
                html_content += "<p>Aucune donnée de carburant disponible.</p>"
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
            <h1>Rapport Carburant de {mois_lettre} {annee}</h1>

            """
            carburant = Carburant.objects.filter(date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)

            # Calculer les totaux de carburant et d'entretien

            for voiture in voitures:
                carburant_voiture = carburant.filter(vehicule=voiture, date_mise_a_jour__month=mois,
                                                     date_mise_a_jour__year=annee)

                html_content += f"""
                                           <h1>Rapport  de {voiture}</h1>
                                         """

                # Vérifier s'il y a des données de carburant pour ce véhicule
                if carburant_voiture:
                    html_content += f"""
                             <table border="1">
                             <tr><th>Date</th><th>Litre</th><th>Prix</th><th>Gestionnaire</th></tr>
                         """

                    for essence in carburant_voiture:
                        if voiture == essence.vehicule:
                            deplacement = Deplacement.objects.filter(vehicule=voiture, date_depart__month=mois,
                                                                     date_depart__year=annee).order_by('date_depart')
                            if deplacement:
                                deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)



                                deplacement_first = deplacement.first()

                                deplacement_last = deplacement.filter(id__in=deplacements_etat_arrive_ids).last()
                                if deplacement_last:
                                    arrive = EtatArrive.objects.filter(deplacement=deplacement_last.id, date_arrive__month=mois,
                                                                       date_arrive__year=annee).last()


                                    total_kilometrage=arrive.kilometrage_arrive-deplacement_first.kilometrage_depart
                                total_carburant = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('prix_total'))[
                                                      'prix_total__sum'] or 0
                                total_quantite = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('quantite'))[
                                                     'quantite__sum'] or 0
                                html_content += f"""
                                        <tr><td>{essence.date_mise_a_jour.date()}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                                    """

                    if deplacement:
                        if deplacement_last:
                            html_content += f"""
                            <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                         <tr> <td colspan="4"><h2>KILOMETRAGE DU VEHICULE:{total_kilometrage}</h2></tr>
                         </table>
                        """

                        else:
                            html_content += f"""
                                        <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                                         <tr> <td colspan="4"><h2>Aucun déplacement effectué</h2></tr>
                                         </table>
                                        """
                    else:
                        html_content += "<p>Aucune donnée de carburant disponible.</p>"
                else:
                        html_content += "<p>Aucune donnée de carburant disponible.</p>"


        # Créer un objet HttpResponse avec le contenu du PDF
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Carburant de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'attachment; filename="Rapport Carburant de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def rapport_carburant_mensuel(request):
    if request.method == 'POST':
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        voiture=Vehicule.objects.all()
        # Filtrer les données de consommation de carburant pour le mois et l'année sélectionnés
        consommations_carburant = Carburant.objects.filter(date_mise_a_jour__month=mois, date_mise_a_jour__year=annee)
        # Calculer la consommation de carburant pour chaque véhicule
        consommations_par_vehicule = {}
        for consommation in consommations_carburant:
            if consommation.vehicule not in consommations_par_vehicule:
                consommations_par_vehicule[consommation.vehicule] = 0
            consommations_par_vehicule[consommation.vehicule] += consommation.quantite

        labels = []
        data = []
        for vehicule, consommation in consommations_par_vehicule.items():
            labels.append(f"{vehicule.marque} - {vehicule.type_commercial}")
            data.append(consommation)

        return render(request, 'rapport_carburant_mensuel.html', {'labels': labels, 'data': data, 'vehicules':voiture})

    return render(request, 'rapport_carburant_mensuel.html')





def rapport_incident_conducteur_mensuel_pdf(request):
    if request.method == 'POST':
        # Récupérez les données soumises du formulaire
        conducteur_id = request.POST.get('conducteur')
        mois = request.POST.get('mois')
        annee = request.POST.get('annee')
        mois_lettre = _(calendar.month_name[int(mois)])
        conducteurs = Conducteur.objects.all()
        if conducteur_id:

            conducteur = Conducteur.objects.get(id=conducteur_id)
            # Récupérer les données de carburant et d'entretien
            incidents = Incident.objects.filter(conducteur=conducteur_id, date_mise_a_jour__month=mois,
                                                date_mise_a_jour__year=annee)

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
                    <h1>Rapport Incident de {mois_lettre} {annee}  de {conducteur}</h1>
                """

            if incidents:
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Vehicule</th><th>Description</th></tr>
                 """
                for incident in incidents:
                    html_content += f"""
                    <tr><td>{incident.date_mise_a_jour.date()}</td><td>{incident.vehicule}</td><td>{incident.description_incident}</td></tr>
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
            incidents = Incident.objects.filter(date_mise_a_jour__month=mois, date_mise_a_jour__year=annee)

            # Vérifier s'il y a des incidents pour ce mois et cette année
            if incidents:

                # Boucle sur chaque conducteur pour générer le rapport
                for conducteur in conducteurs:

                    # Filtrer les incidents pour ce conducteur
                    incidents_conducteur = incidents.filter(conducteur=conducteur)
                    html_content += f"""
                                                                  <h2>Rapport de {conducteur}</h2>
                                                                 
                                                              """

                    # Vérifier s'il y a des incidents pour ce conducteur
                    if incidents_conducteur:
                        html_content += f"""
                                        <table border="1">
                                        <tr><th>Date</th><th>Véhicule</th><th>Description</th></tr>
                                        """

                        # Boucle sur chaque incident pour ce conducteur
                        for incident in incidents_conducteur:
                            html_content += f"""
                                                <tr><td>{incident.date_mise_a_jour.date()}</td><td>{incident.vehicule}</td><td>{incident.description_incident}</td></tr>
                                            """

                            # Calculer le nombre total d'incidents pour ce conducteur
                        total_incident = incidents_conducteur.count()
                        # Calculer les totaux pour ce conducteur
                        total_vehicule = incidents_conducteur.filter(vehicule=incident.vehicule).count()
                        html_content += f"""
                            <tr><td>Total</td><td>{total_vehicule}</td><td>{total_incident}</td></tr>
                        """
                    else:
                        html_content += "<tr><td colspan='3'>Aucun incident trouvé pour ce conducteur.</td></tr>"

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
        if conducteur_id:
            conducteur = Conducteur.objects.get(id=conducteur_id)
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Incident Conducteur de {mois_lettre} {annee}  de {conducteur}.pdf"'
        else:
            response['Content-Disposition'] = f'attachment; filename="Rapport Incident Conducteur de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response
