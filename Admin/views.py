import calendar

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.translation import gettext as _
from datetime import date, datetime

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, ExpressionWrapper, fields, F, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from xhtml2pdf import pisa

from Admin.forms import typeCarburantForm, CarburantSearchForm, UserRegistrationForm
from Model.models import Roles, Utilisateur, type_carburant, periode_carburant, Vehicule, Carburant, Entretien, \
    Deplacement
from utilisateurs.forms import ChangerMotDePasse
from vehicule.forms import VehiculSearchForm
from secrets import compare_digest


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
    return render(request, 'dashoard_admins.html')


def rapport_admins(request):
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport.html', context)


def rapport_mensuel_admins(request):
    vehicule = Vehicule.objects.all()
    context = {'vehicule': vehicule}
    return render(request, 'rapport_mensuel.html', context)


def generate_pdf(request):
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
            entretien = Entretien.objects.filter(vehicule=vehicule_id, date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburant.aggregate(Sum('quantite'))['quantite__sum'] or 0
            nbre_entretien = entretien.count()
            html_content = f"""
                    <html>
                    <head><title>Rapport</title></head>
                    <body>
                    <h1>Rapport de {mois_lettre} {annee}  de {vehicule}</h1>
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
                 <tr><th>Date</th><th>Type</th><th>Prix</th></tr>
                 """
                for reparation in entretien:
                    html_content += f"""
                    <tr><td>{reparation.date_mise_a_jour.date()}</td><td>{reparation.quantite}</td><td>{reparation.prix_total}</td><td>{reparation.utilisateur}</td></tr>
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
            entretien = Entretien.objects.filter(date_mise_a_jour__month=mois,
                                                 date_mise_a_jour__year=annee)

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            # Générer le contenu HTML du PDF
            html_content = f"""
            <html>
            <head><title>Rapport PDF</title></head>
            <body>
            <h1>Rapport Depenses de {mois_lettre} {annee}</h1>
            <table border="1">
            <tr><th>Voitures</th><th>Nombre de déplacements</th><th>Carburant</th><th>Entretien</th><th>Total</th></tr>

            """
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture.id, date_mise_a_jour__month=mois,
                                                     date_mise_a_jour__year=annee)
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture.id, date_mise_a_jour__month=mois,
                                                     date_mise_a_jour__year=annee)
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                vehicule_max_carburant_id = carburant.objects.values('vehicule').annotate(
                    total_carburant=Sum('prix_total')).order_by('-total_carburant').first()
                vehicule_max_entretien_id = entretien.objects.values('vehicule').annotate(
                    total_entretien=Sum('prix_entretient')).order_by('-total_entretien').first()
                deplacement = Deplacement.objects.filter(vehicule=voiture).count()
                nbre_deplacements = +deplacement
                vehicule_max_carburant = Vehicule.objects.get(id=vehicule_max_carburant_id['vehicule'])
                vehicule_max_entretien = Vehicule.objects.get(id=vehicule_max_entretien_id['vehicule'])
                html_content += f"""<tr class="max-total"> <td> {voiture} </td><td> {deplacement} </td><td>{carburant_vehicule}</td><td>{entretien_vehicule}</td><td>{carburant_vehicule + entretien_vehicule}</td></tr>"""


            html_content += f"""
            <tr><td>Total</td><td>{nbre_deplacements}</td><td>{total_carburant}</td><td>{total_entretien}</td><td>{total_carburant + total_entretien}</td></tr>
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
            response['Content-Disposition'] = f'attachment; filename="Rapport de {mois_lettre} {annee}  de {vehicule}.pdf"'
        else:
            response['Content-Disposition'] = f'attachment; filename="Rapport Depenses de {mois_lettre} {annee}.pdf"'
        # Générer le PDF à partir du contenu HTML
        pisa_status = pisa.CreatePDF(html_content, dest=response)
        if pisa_status.err:
            return HttpResponse('Une erreur est survenue lors de la génération du PDF')

        return response


def create_pdf(request):
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
            carburants = Carburant.objects.filter(date_mise_a_jour__date__range=(debut_date, fin_date))
            entretiens = Entretien.objects.filter(date_mise_a_jour__date__range=(debut_date, fin_date))
            total_carburant = carburants.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretiens.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            total_quantite = carburants.aggregate(Sum('quantite'))['quantite__sum'] or 0
            nbre_entretien = entretiens.count()
            html_content = f"""
                               <html>
                               <head><title>Rapport</title></head>
                               <body>
                               <h1>Rapport de {debut_date} à {fin_date}  de {vehicule}</h1>
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
                            <tr><th>Date</th><th>Type</th><th>Prix</th></tr>
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
            entretien = Entretien.objects.filter(date_mise_a_jour__date__range=(debut_date, fin_date))

            # Calculer les totaux de carburant et d'entretien
            total_carburant = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
            total_entretien = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
            # Générer le contenu HTML du PDF
            html_content = f"""
                   <html>
                   <head><title>Rapport PDF</title></head>
                   <body>
                  <h1>Rapport de {debut_date} à {fin_date}</h1>
                   <table border="1">
                   <tr><th>Voitures</th><th>Nombre de deplacement</th><th>Carburant</th><th>Entretien</th><th>Total</th></tr>

                   """
            for voiture in voitures:
                carburant = Carburant.objects.filter(vehicule=voiture.id,
                                                     date_mise_a_jour__date__range=(debut_date, fin_date))
                carburant_vehicule = carburant.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
                entretien = Entretien.objects.filter(vehicule=voiture.id,
                                                     date_mise_a_jour__date__range=(debut_date, fin_date))

                vehicule_max_carburant_id = Carburant.objects.filter(
                    date_mise_a_jour__date__range=(debut_date, fin_date)).values('vehicule').annotate(
                    total_carburant=Sum('prix_total')).order_by('-total_carburant').first()
                if vehicule_max_carburant_id:
                    vehicule_max_carburant = Vehicule.objects.get(id=vehicule_max_carburant_id['vehicule'])
                else:
                    vehicule_max_carburant = "Aucun donné carburant"

                vehicule_max_entretien_id = Entretien.objects.filter(
                    date_mise_a_jour__date__range=(debut_date, fin_date)).values('vehicule').annotate(
                    total_entretien=Sum('prix_entretient')).order_by('-total_entretien').first()
                if vehicule_max_entretien_id:
                    vehicule_max_entretien = Vehicule.objects.get(id=vehicule_max_entretien_id['vehicule'])
                else:
                    vehicule_max_entretien = "Aucun donné carburant"

                deplacement=Deplacement.objects.filter(vehicule=voiture).count()
                nbre_deplacements=+deplacement
                entretien_vehicule = entretien.aggregate(Sum('prix_entretient'))['prix_entretient__sum'] or 0
                html_content += f"""<tr> <td> {voiture} </td><td> {deplacement} </td><td>{carburant_vehicule}</td><td>{entretien_vehicule}</td><td>{carburant_vehicule + entretien_vehicule}</td></tr>"""

            html_content += f"""
                   <tr><td>Total</td><td>{nbre_deplacements}</td><td>{total_carburant}</td><td>{total_entretien}</td><td>{total_carburant + total_entretien}</td></tr>
                   </table>
                   <h1> plus grosse depense en carburant: {vehicule_max_carburant}<h1>
                   <h1>plus grosse depense en entretien:{vehicule_max_entretien}<h1>
                   </body>
                   </html>
                   """
        response = HttpResponse(content_type='application/pdf')
        if vehicule_id:
         vehicule = Vehicule.objects.get(id=vehicule_id)
         response['Content-Disposition'] = f'attachment; filename="Rapport de {debut_date} à {fin_date}  de {vehicule}.pdf"'
        else:
         response['Content-Disposition'] = f'attachment; filename="Rapport de {debut_date} à {fin_date}.pdf"'
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
