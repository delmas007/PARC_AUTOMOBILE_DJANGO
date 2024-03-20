from datetime import date, timedelta
from random import sample
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Subquery
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

import deplacement
from Model.forms import UserRegistrationForm, ConnexionForm
from Model.models import Roles, Utilisateur, Vehicule, Photo, EtatArrive, Deplacement, Demande_prolongement, Entretien
from deplacement.forms import DeplacementSearchForm
from utilisateurs.forms import ConducteurClientForm, PasswordResetForme, ChangerMotDePasse, DemandeProlongementForm, \
    DeclareIncidentForm, notificationSearchForm
from utilisateurs.tokens import account_activation_token
from django.utils.html import strip_tags


# Create your views here.

def Accueil_user(request):
    print("azerty")
    tous_les_vehicule = Vehicule.objects.all()
    vehicules = []
    for vehicule in tous_les_vehicule:
        latest_photo = Photo.objects.filter(vehicule=vehicule).order_by('-id').first()
        vehicules.append({'vehicule': vehicule, 'latest_photo': latest_photo})
    context = {
        'vehicules': vehicules
    }
    return render(request, 'index_user.html', context)


def list_vehicule(request):
    tous_les_vehicule = Vehicule.objects.all()
    vehicules = []
    for vehicule in tous_les_vehicule:
        latest_photo = Photo.objects.filter(vehicule=vehicule).order_by('-id').first()
        vehicules.append({'vehicule': vehicule, 'latest_photo': latest_photo})
    context = {
        'vehicules': vehicules
    }
    return render(request, 'vehicule_list.html', context)


def vehicule_details(request, vehicule_id):
    # photo = get_object_or_404(Photo, pk=vehicule_id)
    photo = Photo.objects.filter(vehicule_id=vehicule_id)
    vehicule = get_object_or_404(Vehicule, pk=vehicule_id)

    context = {'photos': photo, 'vehicule': vehicule}
    return render(request, 'detail.html', context)


def Compte(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            utilisateur = Utilisateur.objects.get(username=request.user.username)
            conducteur_form = ConducteurClientForm(request.POST, request.FILES)
            if conducteur_form.is_valid():
                conducteur_instance = conducteur_form.save()
                utilisateur.conducteur = conducteur_instance
                utilisateur.save()
                messages.success(request, 'Le conducteur a été ajouté avec succès.')
                return redirect('utilisateur:compte')
            else:
                print(conducteur_form.errors)
        else:
            return redirect('utilisateur:connexion_user')
    else:
        conducteur_form = ConducteurClientForm()

    return render(request, 'compte.html', {'conducteur_form': conducteur_form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(mon_uuid=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Merci de votre confirmation par courriel. Vous pouvez maintenant vous connecter à "
                                  "votre compte.")
        return redirect('utilisateur:connexion_user')
    else:
        messages.error(request, "Le lien d’activation est invalide !")

    return redirect('utilisateur:connexion_user')


def activateEmail(request, user, to_email):
    mail_subject = "Activez votre compte utilisateur."
    message = render_to_string("new-email.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.mon_uuid)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http',
        'logo': get_current_site(request).domain + static('image/photo_2023-12-14_15-44-58.ico')
    })
    plain_message = strip_tags(message)
    email = EmailMultiAlternatives(subject=mail_subject, body=plain_message, to=[to_email])
    email.attach_alternative(message, "text/html")
    email.send()
    if email.send():
        messages.success(request, f'Cher <b>{user.nom}</b>, veuillez accéder à votre boîte de réception <b>{to_email}"'
                                  f'</b> et cliquer sur le lien d’activation reçu pour confirmer et compléter '
                                  f'l’enregistrement. <b>Remarque :</b>  Vérifiez votre dossier spam.')
    else:
        messages.error(request,
                       f'Problème d’envoi du courriel à {to_email}, vérifiez si vous l’avez saisi correctement.')


@csrf_protect
def inscription_user(request):
    context = {}
    if request.method == 'POST':
        if 'inscription' in request.POST:
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                client_role = Roles.objects.get(role=Roles.CLIENT)
                user.roles = client_role
                user.is_active = False
                activateEmail(request, user, form.cleaned_data.get('email'))
                user.save()
                return redirect('utilisateur:connexion_user')
            else:

                context['forms'] = form
                return render(request, 'connexion_user.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'connexion_user.html', context=context)


# class Connexion_user(LoginView):
#     template_name = 'connexion_user.html'
#     form_class = ConnexionForm
#
#     def get_success_url(self) -> str:
#         if self.request.user.roles.role == 'CLIENT':
#             return reverse('utilisateur:Accueil_user')
#         if self.request.user.roles.role == 'CONDUCTEUR':
#             return reverse('utilisateur:liste_mission')

# def Connexion_user(request):
#     if request.method == 'POST':
#         if 'connexion' in request.POST:
#             form = ConnexionForm(request, data=request.POST)
#             if form.is_valid():
#                 username = form.cleaned_data.get('username')
#                 password = form.cleaned_data.get('password')
#                 user = authenticate(request, username=username, password=password)
#                 if user is not None:
#                     login(request, user)
#                     role = user.roles.role
#                     if role == 'CLIENT':
#                         return redirect('utilisateur:Accueil_utilisateur')
#                     elif role == 'CONDUCTEUR':
#                         return redirect('utilisateur:liste_mission')
#             else:
#                 return render(request, 'connexion_user.html', {'form': form})
#         else:
#             return inscription_user(request)
#
#     else:
#         form = ConnexionForm()
#         return render(request, 'connexion_user.html', {'form': form})

def Connexion_user(request):
    if request.user.is_authenticated:
        return redirect('utilisateur:liste_mission')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('utilisateur:liste_mission')
        else:
            pass

    return render(request, 'connexion_user.html')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForme(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("reinitialisation.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.mon_uuid)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                plain_message = strip_tags(message)
                email = EmailMultiAlternatives(subject=subject, body=plain_message, to=[associated_user.email])
                email.attach_alternative(message, "text/html")
                email.send()
                if email.send():
                    messages.success(request,
                                     """
                                     <h4>Réinitialisation du mot de passe envoyée</h4><hr>
                                     <p>
                                         Nous vous avons envoyé les instructions par e-mail pour définir votre mot de passe. Si un compte existe avec l’e-mail que vous avez entré,
                                          vous devriez les recevoir sous peu. <br>Si vous ne recevez pas le courriel, veuillez vous assurer d’avoir saisi l’adresse e-mail avec 
                                          laquelle vous vous êtes inscrit(e) et vérifiez votre dossier spam.
                                     </p>
                                     """
                                     )
                else:
                    messages.error(request, "Problème d’envoi de l’e-mail de réinitialisation du mot de passe, "
                                            "<b>PROBLÈME SERVEUR</b>")

            return redirect('Model:connexion')

    form = PasswordResetForme()
    return render(
        request=request,
        template_name="email.html",
        context={"form": form}
    )


def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(mon_uuid=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ChangerMotDePasse(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Votre mot de passe a été défini. Vous pouvez continuer et <b>vous "
                                          "connecter </b> maintenant.")
                return redirect('Model:connexion')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = ChangerMotDePasse(user)
        return render(request, 'password.html', {'form': form})
    else:
        messages.error(request, "Le lien a expiré")

    messages.error(request, 'Quelque chose a mal tourné, rediriger vers la page d’accueil')
    return redirect("Accueil")


@login_required(login_url='utilisateur:connexion_user')
def liste_mission(request):
    prolongement = Demande_prolongement.objects.filter(accepter=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_accepter = Demande_prolongement.objects.filter(accepter=True)
    prolongement_refuse = Demande_prolongement.objects.filter(refuser=True)
    date_aujourdui = date.today()
    # Récupérer l'utilisateur actuellement connecté
    utilisateur_actif = request.user

    # Récupérer l'ID du conducteur actif à partir de l'utilisateur actif
    conducteur_actif_id = utilisateur_actif.conducteur_id

    # Récuperation des id de de demande de prolongement dans une liste
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    prolongement_accepter_ids = prolongement_accepter.values_list('deplacement_id', flat=True)
    prolongement_refuse_ids = prolongement_refuse.values_list('deplacement_id', flat=True)
    # Récupérer une sous-requête avec les IDs des déplacements ayant un état d'arrivée
    deplacements_arrives_ids = EtatArrive.objects.values('deplacement_id')

    # Exclure les déplacements avec leurs IDs dans la sous-requête
    mission_list = Deplacement.objects.exclude(id__in=Subquery(deplacements_arrives_ids)).filter(
        conducteur_id=conducteur_actif_id).order_by('date_depart')

    return render(request, 'compte_conducteur.html', {'mission': mission_list, 'date_aujourdui': date_aujourdui,
                                                      'prolongement_encours': prolongement_encours_ids,
                                                      'prolongement_accepter': prolongement_accepter_ids,
                                                      'prolongement_refuse': prolongement_refuse_ids,
                                                      'prolongement': prolongement, })


def prolongement(request):
    if request.method == 'POST':
        form = DemandeProlongementForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) <= 6:
                demande_prolongement = form.save(commit=False)
                utilisateur_actif = request.user
                conducteur_actif_id = utilisateur_actif.conducteur_id
                demande_prolongement.conducteur_id = conducteur_actif_id
                deplacement_id = form.cleaned_data['deplacement_id']
                deplacement = Deplacement.objects.get(id=deplacement_id)
                demande_prolongement.deplacement = deplacement
                demande_prolongement.save()

                for uploaded_file in images:
                    photo = Photo.objects.create(demande_prolongement=demande_prolongement, images=uploaded_file)

                messages.success(request, 'Le prolongement a été ajouté avec succès.')
            return redirect('utilisateur:liste_mission')
        else:
            print(form.errors)
    else:
        form = DemandeProlongementForm()
    return render(request, 'compte_conducteur.html', {'form': form})


@login_required
def liste_demandes(request):
    utilisateur_actif = request.user
    conducteur_actif = utilisateur_actif.conducteur_id
    arrive_list_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    demande_list = Demande_prolongement.objects.filter(conducteur_id=conducteur_actif).exclude(
        deplacement__in=arrive_list_ids)
    paginator = Paginator(demande_list.order_by('date_mise_a_jour'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        demande_list = paginator.page(page)
    except EmptyPage:
        demande_list = paginator.page(paginator.num_pages())

        print(demande_list)

    return render(request, 'compte_conducteur.html', {'demande': demande_list})


def declare_incident(request):
    date_aujourdui = date.today()
    # Récupérer l'utilisateur actuellement connecté
    utilisateur_actif = request.user

    # Récupérer l'ID du conducteur actif à partir de l'utilisateur actif
    conducteur_actif_id = utilisateur_actif.conducteur_id

    deplacements_arrives_ids = EtatArrive.objects.values('deplacement_id')

    # Exclure les déplacements avec leurs IDs dans la sous-requête
    mission_list = Deplacement.objects.filter(conducteur_id=conducteur_actif_id).filter(
        date_depart__lte=date_aujourdui).exclude(id__in=Subquery(deplacements_arrives_ids))

    paginator = Paginator(mission_list.order_by('date_depart'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        mission_list = paginator.page(page)
    except EmptyPage:
        mission_list = paginator.page(paginator.num_pages())

    return render(request, 'compte_conducteur.html', {'mission': mission_list})


def sendIncident(request):
    if request.method == 'POST':
        form = DeclareIncidentForm(request.POST, request.FILES)

        if form.is_valid():

            images = request.FILES.getlist('images')
            if len(images) <= 6:
                incident = form.save(commit=False)
                utilisateur_actif = request.user
                conducteur_actif_id = utilisateur_actif.conducteur_id
                incident.conducteur_id = conducteur_actif_id

                # Maintenant, vous pouvez obtenir le véhicule du formulaire
                vehicule_id = form.cleaned_data['vehicule_id']
                deplacement_id = form.cleaned_data['deplacement2_id']
                deplacement = Deplacement.objects.get(id=deplacement_id)
                incident.vehicule = Vehicule.objects.get(id=vehicule_id.id)
                incident.deplacement = deplacement

                incident.save()

                for uploaded_file in images:
                    photo = Photo.objects.create(incident=incident, images=uploaded_file)

                messages.success(request, 'Le prolongement a été ajouté avec succès.')

            return redirect('utilisateur:declare_incident')
        else:
            print(form.errors)
    else:
        form = DeclareIncidentForm()

    return render(request, 'compte_conducteur.html', {'form': form})


def ChangerMotDePassee(request):
    if request.method == 'POST':
        form = ChangerMotDePasse(request.user, request.POST)
        print(request.POST.get('passe'))
        print(request.user.check_password(request.POST.get('passe')))
        if request.user.check_password(request.POST.get('passe')):
            print('1111')
            if form.is_valid():
                print('2222')
                form.save()
                messages.success(request, "Votre mot de passe a été changer.")
                return redirect('Connexion')
            else:
                messages.error(request, "Les deux mots de passe ne correspondent pas")
        else:
            messages.error(request, "Le mot de passe actuel est incorrect.")
    form = ChangerMotDePasse(request.user)
    return render(request, 'changerMotDePasse.html', {'form': form})


def ChangerMotDePasseConducteur(request):
    if request.method == 'POST':
        form = ChangerMotDePasse(request.user, request.POST)
        print(request.POST.get('passe'))
        print(request.user.check_password(request.POST.get('passe')))
        if request.user.check_password(request.POST.get('passe')):
            print('1111')
            if form.is_valid():
                print('2222')
                form.save()
                messages.success(request, "Votre mot de passe a été changer.")
                return redirect('utilisateur:connexion_user')
            else:
                messages.error(request, "Les deux mots de passe ne correspondent pas")
        else:
            messages.error(request, "Le mot de passe actuel est incorrect.")
    form = ChangerMotDePasse(request.user)
    return render(request, 'compte_conducteur.html', {'form': form})


def ProfilUser(request):
    return render(request, 'Profil_user.html')


# def ChangerMotDePassee(request):
#     if request.method == 'POST':
#         form = ChangerMotDePasse(request.user, request.POST)
#         if request.user.check_password(form.cleaned_data['passe']):
#             if form.is_valid():
#                 user = request.user
#                 old_password = form.cleaned_data['passe']
#                 new_password1 = form.cleaned_data['new_password1']
#                 new_password2 = form.cleaned_data['new_password2']
#
#                 # Vérifier si le mot de passe actuel est correct
#                 if user.check_password(old_password):
#                     # Vérifier si les nouveaux mots de passe correspondent
#                     if new_password1 == new_password2:
#                         # Définir le nouveau mot de passe et sauvegarder l'utilisateur
#                         user.set_password(new_password1)
#                         user.save()
#
#                         # Mise à jour de la session de l'authentification pour éviter la déconnexion de l'utilisateur
#                         update_session_auth_hash(request, user)
#
#                         messages.success(request, "Votre mot de passe a été modifié avec succès.")
#                         return redirect('Model:connexion')
#                     else:
#                         messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
#                 else:
#                     messages.error(request, "Le mot de passe actuel est incorrect.")
#             else:
#                 for error in list(form.errors.values()):
#                     messages.error(request, error)
#
#                 print(form.errors)
#     else:
#         form = ChangerMotDePasse(request.user)
#     return render(request, 'changerMotDePasse.html', {'form': form})

# def deplacement_s(request, prolongement_id):
#     form = DeplacementSearchForm(request.GET)
#     aujourdhui = date.today()
#     deplacement = Deplacement.objects.filter(date_depart__gte=aujourdhui)
#
#     if form.is_valid():
#         if prolongement_id:
#             deplacement = deplacement.filter(Q(conducteur__demande_prolongement=prolongement_id))
#
#     paginator = Paginator(deplacement.order_by('date_mise_a_jour'), 5)
#     page = request.GET.get("page", 1)
#     try:
#         deplacements = paginator.page(page)
#     except EmptyPage:
#         deplacements = paginator.page(paginator.num_pages)
#
#     context = {'deplacements': deplacements, 'form': form}
#
#     # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
#     if deplacement.count() == 0 and form.is_valid():
#         context['no_results'] = True
#
#     return render(request, 'afficher_deplacement_en_cours.html', context)


def deplacement_s(request, prolongement_nom):
    form = DeplacementSearchForm(request.GET)
    aujourdhui = date.today()
    deplacements_etat_arrive_ids = EtatArrive.objects.values_list('deplacement_id', flat=True)
    deplacement = Deplacement.objects.filter(date_depart__lte=aujourdhui).exclude(
        Q(id__in=deplacements_etat_arrive_ids))
    prolongement = Demande_prolongement.objects.all()

    deplacements = Deplacement.objects.filter(Q(date_depart__lte=aujourdhui)).exclude(
        Q(id__in=deplacements_etat_arrive_ids))
    deplacement_ids = deplacements.values_list('id', flat=True)
    prolongement_encours = Demande_prolongement.objects.filter(en_cours=True)
    prolongement_arrive = Demande_prolongement.objects.filter(refuser=True)
    prolongement_accepte = Demande_prolongement.objects.filter(accepter=True)

    # recuperer liste des id de demandes de prolongement
    prolongement_encours_ids = prolongement_encours.values_list('deplacement_id', flat=True)
    prolongement_arrive_ids = prolongement_arrive.values_list('deplacement_id', flat=True)
    prolongement_accepte_ids = prolongement_accepte.values_list('deplacement_id', flat=True)

    if form.is_valid():
        query = f'{prolongement_nom}'
        print(f'{prolongement_nom}')
        if query:
            query_parts = query.split()
            if len(query_parts) > 1:
                nom = query_parts[0]  # First part is considered the last name (nom)
                prenoms = query_parts[1:]  # All parts except the first one are considered first names (prenoms)
                # Recherchez le nom
                deplacement = deplacement.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=nom)
                )
                # Filter by each first name (prenoms)
                for prenom in prenoms:
                    deplacement = deplacement.filter(conducteur__utilisateur__prenom__icontains=prenom)
            else:
                # Si la requête ne contient pas exactement deux parties, recherchez normalement
                deplacement = deplacement.filter(
                    Q(vehicule__marque__marque__icontains=query) |
                    Q(conducteur_id=query) |
                    Q(vehicule__numero_immatriculation__icontains=query) |
                    Q(vehicule__type_commercial__modele__icontains=query) |
                    Q(conducteur__utilisateur__nom__icontains=query) |
                    Q(conducteur__utilisateur__prenom__icontains=query)
                )

    paginator = Paginator(deplacement.order_by('date_mise_a_jour'), 5)
    page = request.GET.get("page", 1)
    try:
        deplacements = paginator.page(page)
    except EmptyPage:
        deplacements = paginator.page(paginator.num_pages)

    context = {'deplacements': deplacements, 'form': form,
               'deplacement': deplacement, 'prolongement_encours': prolongement_encours_ids,
               'prolongement_arrive': prolongement_arrive_ids, 'prolongement_accepte': prolongement_accepte_ids,
               'prolongements': prolongement}

    # Ajouter la logique pour gérer les cas où aucun résultat n'est trouvé
    if deplacement.count() == 0 and form.is_valid():
        context['no_results'] = True

    return render(request, 'afficher_deplacement_en_cours.html', context)
