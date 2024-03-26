import calendar
import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.timezone import now
from django.utils.translation import gettext as _
from datetime import date, datetime

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, ExpressionWrapper, fields, F, Sum, Count, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from xhtml2pdf import pisa

from Admin.forms import typeCarburantForm, CarburantSearchForm, UserRegistrationForm
from Admin.views2 import courbe_depense_mensuel, courbe_depense_global, courbe_incident_conducteur_mensuel
from Model.models import Roles, Utilisateur, type_carburant, periode_carburant, Vehicule, Carburant, Entretien, \
    Deplacement, Conducteur, Incident, EtatArrive, Demande_prolongement
from utilisateurs.forms import ChangerMotDePasse
from vehicule.forms import VehiculSearchForm
from secrets import compare_digest
from django.http import JsonResponse
from django.utils.timezone import now


@login_required(login_url='Connexion')
@csrf_protect
def inscription(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
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


@login_required(login_url='Connexion')
def employer_compte(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')

    gestionnaires = (
        Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())).order_by('-hour')
        )

    paginator = Paginator(gestionnaires, 4)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        gestionnaires = paginator.page(page)
    except EmptyPage:
        gestionnaires = paginator.page(paginator.num_pages())

    return render(request, 'tous_les_gestionnaires.html', {'gestionnaires': gestionnaires})


@login_required(login_url='Connexion')
def gestionnaire_inactifs(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')

    gestionnaires2 = (
        Utilisateur.objects.filter(roles__role__in=[Roles.GESTIONNAIRE], is_active=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())).order_by('-hour')
        )

    paginator = Paginator(gestionnaires2, 4)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        gestionnaires2 = paginator.page(page)
    except EmptyPage:
        gestionnaires2 = paginator.page(paginator.num_pages())

    return render(request, 'tous_les_gestionnairess.html', {'gestionnaires2': gestionnaires2})


@login_required(login_url='Connexion')
def active_emp(request, employer_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()
    return redirect('admins:gestionnaire_inactifs')


@login_required(login_url='Connexion')
def desactive_amp(request, employer_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_gestionnaire')


@login_required(login_url='Connexion')
def gestionnaire_a_search(request):
    form = VehiculSearchForm(request.GET)

    gestionnaire = (
        Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=False).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())).order_by('-hour')
        )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        paginator = Paginator(gestionnaire, 4)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            gestionnaire = paginator.page(page)
        except EmptyPage:
            gestionnaire = paginator.page(paginator.num_pages())

        context = {'gestionnaires': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnaires.html', context)


@login_required(login_url='Connexion')
def gestionnaire_a_search_i(request):
    form = VehiculSearchForm(request.GET)

    gestionnaire = (
        Utilisateur.objects.filter(roles__role='GESTIONNAIRE').exclude(is_active=True).annotate(
            hour=ExpressionWrapper(F('date_mise_a_jour'), output_field=fields.TimeField())).order_by('-hour')
        )

    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            gestionnaire = gestionnaire.filter(Q(nom__icontains=query) |
                                               Q(email__icontains=query) |
                                               Q(prenom__icontains=query))

        paginator = Paginator(gestionnaire, 4)
        try:
            page = request.GET.get("page")
            if not page:
                page = 1
            gestionnaire = paginator.page(page)
        except EmptyPage:
            gestionnaire = paginator.page(paginator.num_pages())

        context = {'gestionnaires2': gestionnaire, 'form': form}
        # Ajoutez la logique pour gérer les cas où aucun résultat n'est trouvé
        if not gestionnaire and form.is_valid():
            context['no_results'] = True

    return render(request, 'tous_les_gestionnairess.html', context)


@login_required(login_url='Connexion')
def Ajouter_Carburant(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
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


@login_required(login_url='Connexion')
def liste_Carburant(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
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


@login_required(login_url='Connexion')
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


@login_required(login_url='Connexion')
def dashboard_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    aujourd_hui = date.today()
    nombre_deplacements_en_cours = Deplacement.objects.filter(Q(date_depart__lte=aujourd_hui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids)).count()

    nombre_vehicules = Vehicule.objects.filter(supprimer=False).count()
    incidents_externe = Incident.objects.filter(conducteur_id__isnull=False).count()
    incidents_interne = Incident.objects.filter(conducteur_id__isnull=True).count()
    nombre_incidents = incidents_interne + incidents_externe
    vehicules_ids_with_carburant = Carburant.objects.values('vehicule_id').distinct()
    vehicles = Vehicule.objects.filter(id__in=Subquery(vehicules_ids_with_carburant))
    vehicules = Vehicule.objects.all()
    labels = [f"{vehicle.marque} {vehicle.type_commercial}" for vehicle in vehicles]
    mois = date.today().month
    mois_ = _(calendar.month_name[int(mois)])
    mois_lettre = mois_.upper()
    annee = date.today().year
    fuel_data = [vehicle.total_carburant(mois, annee) for vehicle in vehicles]
    quantites = [data['quantite'] for data in fuel_data]
    prix = [data['prix'] for data in fuel_data]

    types_carburant = type_carburant.objects.all()

    totals_carburant = []
    label = [carburant.nom for carburant in types_carburant]
    for carburant in types_carburant:
        total_quantite = Carburant.objects.filter(type=carburant).aggregate(Sum('quantite'))['quantite__sum'] or 0
        totals_carburant.append(total_quantite)
    deplacements_par_vehicule = []
    for vehicle in vehicules:
        total_deplacements_mois = vehicle.deplacement_set.filter(
            date_depart__month=mois,
            date_depart__year=annee,
            id__in=deplacements_etat_arrive_ids
        ).count()
        if total_deplacements_mois:
            deplacements_par_vehicule.append({'vehicle': vehicle, 'total_deplacements_mois': total_deplacements_mois})

    context = {
        'labels_circ': label,
        'labels': labels,
        'data': totals_carburant,
        'quantites': quantites,
        'prix': prix,
        'mois': mois_lettre,
        'nombre_vehicules': nombre_vehicules,
        'nombre_incidents': nombre_incidents,
        'nombre_deplacements_en_cours': nombre_deplacements_en_cours,
        'labels_entr': labels,
        'deplacements_par_vehicule': deplacements_par_vehicule,
    }

    return render(request, 'dashoard_admins.html', context)


@login_required(login_url='Connexion')
def rapport_depense_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_depense_global(request)
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_depense.html', context)


@login_required(login_url='Connexion')
def rapport_depense_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_depense_mensuel(request)
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_depense_mensuel.html', context)


@login_required(login_url='Connexion')
def rapport_carburant_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return rapport_carburant_mensuel(request)
    else:
        vehicules = Vehicule.objects.all()
        context = {'vehicules': vehicules}
        return render(request, 'rapport_carburant_mensuel.html', context)


@login_required(login_url='Connexion')
def rapport_incident_conducteur_mensuel_admins(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        return courbe_incident_conducteur_mensuel(request)
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
        variations = periode_carburant.objects.all()
        types = type_carburant.objects.all()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            # Récupérer les données de carburant et d'entretien
            carburant = Carburant.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                 date_premiere__year=annee)
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
                                page-break-inside: avoid;
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
                    <tr><td>{essence.date_premiere}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                """
                html_content += f"""

                <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                 </table>
                """
                variation_first = variations.filter(carburant_id=vehicule.energie.id, date_debut__month__lte=mois,
                                                    date_debut__year__lte=annee).order_by('date_debut')

                html_content += f"""
                <br>
                <br>
                <br>
                <h1> VARIATION DES PRIX DU {vehicule.energie.nom.upper()}
                                                                 <table border="1">
                                                                 <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                                 """
                for variation in variation_first:
                    date_fin_info = ""
                    if variation.date_fin:
                        date_fin_info = f" au {variation.date_fin.date()}"
                    if variation.date_fin:
                        if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                annee) or not variation.date_fin:
                            html_content += f"""
                                       <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation.date_debut.date()} {date_fin_info}</td></tr>
                                                       """
                    else:
                        html_content += f"""
                                       <tr>
                                           <td>{variation.carburant.nom}</td>
                                           <td>{variation.prix}</td>
                                           <td>{variation.date_debut.date()} {date_fin_info}</td>
                                       </tr>
                                   """
                html_content += f"""
                           </table>"""
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
                    <tr><td>{reparation.date_entretien}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                """
                html_content += f"""

                <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                 </table>
                """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"

            if carburant and entretien:
                html_content += f"""
                <table border="1" style="margin-top:20px">
                <tr colspan="3"><td>TOTAL DEPENSE</td><td>{total_entretien + total_carburant}</td></tr>
                 </table>
                           """
        else:
            carburant = Carburant.objects.filter(date_premiere__month=mois,
                                                 date_premiere__year=annee)
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
                carburant = Carburant.objects.filter(vehicule=voiture, date_premiere__month=mois,
                                                     date_premiere__year=annee)
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                carburant_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture, date_entretien__month=mois,
                                                     date_entretien__year=annee)
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                vehicule_max_carburant_id = Carburant.objects.values('vehicule').annotate(
                    total_carburant=Sum('prix_total')).order_by('-total_carburant').first()
                vehicule_max_entretien_id = Entretien.objects.values('vehicule').annotate(
                    total_entretien=Sum('prix_entretient')).order_by('-total_entretien').first()
                deplacement = Deplacement.objects.filter(vehicule=voiture, date_depart__month=mois,
                                                         date_depart__year=annee).count()
                nbre_deplacements += deplacement
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
            if carburant:
                for type in types:
                    variation_first = variations.filter(carburant=type, date_debut__month__lte=mois,
                                                        date_debut__year__lte=annee).order_by('date_debut')

                    html_content += f"""
                    <br>
                    <br>
                    <br>
                    <h1>VARIATION DES PRIX DU {type.nom.upper()}</h1>
                    <br>
                                                                                        <table border="1">
                                                                                        <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                                                        """
                    for variation in variation_first:
                        date_fin_info = ""
                        if variation.date_fin:
                            date_fin_info = f" au {variation.date_fin.date()}"
                        if variation.date_fin:
                            if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                    annee) or not variation.date_fin:
                                html_content += f"""
                                                                             <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation.date_debut.date()} {date_fin_info}</td></tr>
                                                                                             """
                        else:
                            html_content += f"""
                                                                             <tr>
                                                                                 <td>{variation.carburant.nom}</td>
                                                                                 <td>{variation.prix}</td>
                                                                                 <td>{variation.date_debut.date()} {date_fin_info}</td>
                                                                             </tr>
                                                                         """
                    html_content += f"""
                                                                 </table>"""
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
        variations = periode_carburant.objects.all()
        types = type_carburant.objects.all()

        if fin:
            fin_date = datetime.strptime(fin, '%Y-%m-%d').date()
        else:
            fin_date = date.today()
        if vehicule_id:

            vehicule = Vehicule.objects.get(id=vehicule_id)
            carburants = Carburant.objects.filter(vehicule=vehicule,
                                                  date_premiere__range=(debut_date, fin_date))
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
                                       page-break-inside: avoid;
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
                               <tr><td>{essence.date_premiere}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
                           """
                html_content += f"""

                           <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                            </table>
                           """
                variation_first = variations.filter(carburant_id=vehicule.energie.id,
                                                    date_debut__lte=fin_date).order_by('date_debut')

                html_content += f"""
                               <br>
                               <br>
                               <br>
                               <h1> VARIATION DES PRIX DU {vehicule.energie.nom.upper()}
                                                                                <table border="1">
                                                                                <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                                                """
                for variation in variation_first:
                    date_fin_info = ""
                    if variation.date_fin:
                        date_fin_info = f" au {variation.date_fin.date()}"
                    if variation.date_fin:
                        if debut_date <= variation.date_fin.date() <= fin_date or not variation.date_fin:
                            html_content += f"""
                                                      <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation.date_debut.date()} {date_fin_info}</td></tr>
                                                                      """
                    else:
                        html_content += f"""
                                                      <tr>
                                                          <td>{variation.carburant.nom}</td>
                                                          <td>{variation.prix}</td>
                                                          <td>{variation.date_debut.date()} {date_fin_info}</td>
                                                      </tr>
                                                  """
                html_content += f"""
                                          </table>"""
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
                               <tr><td>{reparation.date_entretien}</td><td>{reparation.type}</td><td>{reparation.prix_entretient}</td><td>{reparation.utilisateur}</td></tr>
                           """
                html_content += f"""

                           <tr><td>Total</td><td>{nbre_entretien}</td><td>{total_entretien}</td></tr>
                            </table>
                           """
            if carburants and entretiens:
                html_content += f"""
                <table border="1" style="margin-top:20px">
                <tr colspan="3"><td>TOTAL DEPENSE</td><td>{total_entretien + total_carburant}</td></tr>
                 </table>
                           """
            else:
                html_content += "<p>Aucune donnée d'entretien disponible.</p>"
        else:
            carburant = Carburant.objects.filter(date_premiere__range=(debut_date, fin_date))
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
                  <tr><th>Voitures</th><th>Nombre de deplacements</th><th>Quantitié de carburant</th><th>Carburant</th><th>Nombre 
                  entretien</th><th>Entretien</th><th>Total</th></tr>

                   """
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture,
                                                     date_premiere__range=(debut_date, fin_date))
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                carburant_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture,
                                                     date_entretien__range=(debut_date, fin_date))
                nbre_entretien = entretien.count()
                nbres_entretien += nbre_entretien
                vehicule_max_carburant_id = Carburant.objects.filter(
                    date_premiere__range=(debut_date, fin_date)).values('vehicule').annotate(
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

                deplacement = Deplacement.objects.filter(vehicule=voiture,
                                                         date_depart__range=(debut_date, fin_date)).count()
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
            if carburant:
                for type in types:
                    variation_first = variations.filter(carburant=type, date_debut__lte=fin_date).order_by('date_debut')

                    html_content += f"""
                    <br>
                    <br>
                    <br>
                    <h1>VARIATION DES PRIX DU {type.nom.upper()}</h1>
                    <br>
                                                                                        <table border="1">
                                                                                        <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                                                        """
                    for variation in variation_first:
                        date_fin_info = ""
                        if variation.date_fin:
                            date_fin_info = f" au {variation.date_fin.date()}"
                        if variation.date_fin:
                            if debut_date <= variation.date_fin.date() <= fin_date or not variation.date_fin:
                                html_content += f"""
                                                                             <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation.date_debut.date()} {date_fin_info}</td></tr>
                                                                                             """
                        else:
                            html_content += f"""
                                                                             <tr>
                                                                                 <td>{variation.carburant.nom}</td>
                                                                                 <td>{variation.prix}</td>
                                                                                 <td>{variation.date_debut.date()} {date_fin_info}</td>
                                                                             </tr>
                                                                         """
                    html_content += f"""
                                                                 </table>"""

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


@login_required(login_url='Connexion')
def CustomPasswordResetConfirmView(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
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


@login_required(login_url='Connexion')
def ChangerMotDePasse_admin(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
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
        variations = periode_carburant.objects.all()
        types = type_carburant.objects.all()
        if vehicule_id:

            carburant = Carburant.objects.filter(vehicule=vehicule_id, date_premiere__month=mois,
                                                 date_premiere__year=annee)

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

                    total_kilometrage = arrive.kilometrage_arrive - deplacement_first.kilometrage_depart

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
                    <tr><td>{essence.date_premiere}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
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
                         <br>
                         <br>
                         <br>
                        """
                else:
                    html_content += f"""
                        <tr><td>Total</td><td>{total_quantite}</td><td>{total_carburant}</td></tr>
                         <tr> <td colspan="4"><h2>Aucun déplacement effectué</h2></tr>
                         </table>
                         <br>
                         <br>
                         <br>
                        """
                variation_first = variations.filter(carburant_id=vehicule.energie.id, date_debut__month__lte=mois,
                                                    date_debut__year__lte=annee).order_by('date_debut')

                html_content += f"""
                <h1>VARIATION DES PRIX DU {vehicule.energie.nom.upper()}</h1>
                                                  <table border="1">
                                                  <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                  """
                for variation in variation_first:
                    date_fin_info = ""
                    if variation.date_fin:
                        date_fin_info = f" au {variation.date_fin.date()}"
                    if variation.date_fin:
                        if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                annee) or not variation.date_fin:
                            html_content += f"""
                                       <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation.date_debut.date()} {date_fin_info}</td></tr>
                                                       """
                    else:
                        html_content += f"""
                                       <tr>
                                           <td>{variation.carburant.nom}</td>
                                           <td>{variation.prix}</td>
                                           <td>{variation.date_debut.date()} {date_fin_info}</td>
                                       </tr>
                                   """
                html_content += f"""
                           </table>"""
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
                                 page-break-inside: avoid;
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
            carburant = Carburant.objects.filter(date_premiere__month=mois,
                                                 date_premiere__year=annee)

            # Calculer les totaux de carburant et d'entretien

            for voiture in voitures:
                carburant_voiture = carburant.filter(vehicule=voiture, date_premiere__month=mois,
                                                     date_premiere__year=annee)

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
                                deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id',
                                                                                              flat=True)

                                deplacement_first = deplacement.first()

                                deplacement_last = deplacement.filter(id__in=deplacements_etat_arrive_ids).last()
                                if deplacement_last:
                                    arrive = EtatArrive.objects.filter(deplacement=deplacement_last.id,
                                                                       date_arrive__month=mois,
                                                                       date_arrive__year=annee).last()

                                    total_kilometrage = arrive.kilometrage_arrive - deplacement_first.kilometrage_depart
                            total_carburant = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('prix_total'))[
                                                  'prix_total__sum'] or 0
                            total_quantite = carburant_voiture.filter(vehicule=voiture).aggregate(Sum('quantite'))[
                                                 'quantite__sum'] or 0
                            html_content += f"""
                                        <tr><td>{essence.date_premiere}</td><td>{essence.quantite}</td><td>{essence.prix_total}</td><td>{essence.utilisateur}</td></tr>
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
                         <tr> <td colspan="4"><h2>Aucun deplacement effectué.</h2></tr>
                         </table>
                        """

                else:
                    html_content += f""" \
                                    <table border="1" >
                                    <tr> <td colspan="4"><h2>Aucune donnée de carburant disponible.</h2></tr>
                         </table>"""

            if carburant:
                for type in types:
                    variation_first = variations.filter(carburant=type, date_debut__month__lte=mois,
                                                        date_debut__year__lte=annee).order_by('date_debut')

                    html_content += f"""
                    <br>
                    <br>
                    <br>
                    <h1>VARIATION DES PRIX DU {type.nom.upper()}</h1>
                    <br>
                                                                                        <table border="1">
                                                                                        <tr><th>NOM</th><th>PRIX</th><th>PRERIODE</th></tr>
                                                                                        """
                    for variation in variation_first:
                        date_fin_info = ""
                        if variation.date_fin:
                            date_fin_info = f" au {variation.date_fin.date()}"
                        if variation.date_fin:
                            if variation.date_fin.month == int(mois) and variation.date_fin.year == int(
                                    annee) or not variation.date_fin:
                                html_content += f"""
                                                                             <tr><td>{variation.carburant.nom}</td><td>{variation.prix}</td><td>{variation.date_debut.date()} {date_fin_info}</td></tr>
                                                                                             """
                        else:
                            html_content += f"""
                                                                             <tr>
                                                                                 <td>{variation.carburant.nom}</td>
                                                                                 <td>{variation.prix}</td>
                                                                                 <td>{variation.date_debut.date()} {date_fin_info}</td>
                                                                             </tr>
                                                                         """
                    html_content += f"""
                                                                 </table>"""

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


@login_required(login_url='Connexion')
def rapport_carburant_mensuel(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('utilisateur:erreur')
    if request.method == 'POST':
        mois = request.POST.get('mois')
        mois_lettre = _(calendar.month_name[int(mois)])
        annee = request.POST.get('annee')
        vehicules_ids_with_carburant = Carburant.objects.values('vehicule_id').distinct()
        vehicule = Vehicule.objects.filter(id__in=Subquery(vehicules_ids_with_carburant))
        voiture = Vehicule.objects.all()
        labels = [f"{vehicle}" for vehicle in vehicule]
        fuel_data = [vehicle.total_carburant(mois, annee) for vehicle in vehicule]
        quantites = [data['quantite'] for data in fuel_data]
        prix = [data['prix'] for data in fuel_data]

        context = {
            'labels': labels,
            'quantites': quantites,
            'prix': prix,
            'vehicules': voiture,
            'mois': mois_lettre,
            'annee': annee
        }

        return render(request, 'rapport_carburant_mensuel.html', context)

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
            incidents = Incident.objects.filter(conducteur=conducteur_id, date_premiere__month=mois,
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
                    <h1>Rapport Incident de {mois_lettre} {annee}  de {conducteur}</h1>
                """

            if incidents:
                html_content += """
                 <table border="1">
                 <tr><th>Date</th><th>Vehicule</th><th>Description</th></tr>
                 """
                for incident in incidents:
                    html_content += f"""
                    <tr><td>{incident.date_premiere}</td><td>{incident.vehicule}</td><td>{incident.description_incident}</td></tr>
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
                                                <tr><td>{incident.date_premiere}</td><td>{incident.vehicule}</td><td>{incident.description_incident}</td></tr>
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
            response[
                'Content-Disposition'] = f'attachment; filename="Rapport Incident Conducteur de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response
