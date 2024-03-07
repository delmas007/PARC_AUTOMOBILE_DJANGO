from datetime import date
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
from Model.forms import UserRegistrationForm, ConnexionForm
from Model.models import Roles, Utilisateur, Vehicule, Photo, EtatArrive, Deplacement, Demande_prolongement
from utilisateurs.forms import ConducteurClientForm, PasswordResetForme, ChangerMotDePasse, DemandeProlongementForm, \
    DeclareIncidentForm
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

def Connexion_user(request):
    if request.method == 'POST':
        if 'connexion' in request.POST:
            form = ConnexionForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    role = user.roles.role
                    if role == 'CLIENT':
                        return redirect('utilisateur:Accueil_utilisateur')
                    elif role == 'CONDUCTEUR':
                        return redirect('utilisateur:liste_mission')
            else:
                return render(request, 'connexion_user.html', {'form': form})
        else:
            return inscription_user(request)

    else:
        form = ConnexionForm()
        return render(request, 'connexion_user.html', {'form': form})


def Acceuil_conducteur(request):
    return render(request, 'ut')


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


@login_required
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
        conducteur_id=conducteur_actif_id)

    paginator = Paginator(mission_list.order_by('date_depart'), 3)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        mission_list = paginator.page(page)
    except EmptyPage:
        mission_list = paginator.page(paginator.num_pages())

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
    arrive_list_ids=EtatArrive.objects.values_list('deplacement_id', flat=True)
    demande_list = Demande_prolongement.objects.filter(conducteur_id=conducteur_actif).exclude(deplacement__in=arrive_list_ids)
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
    mission_list = Deplacement.objects.filter(conducteur_id=conducteur_actif_id).filter(date_depart__lte=date_aujourdui).exclude(id__in=Subquery(deplacements_arrives_ids))

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
                deplacement_id = form.cleaned_data['deplacement_id']
                deplacement = Deplacement.objects.get(id=deplacement_id)
                incident.vehicule = deplacement.vehicule
                incident.save()

                for uploaded_file in images:
                    photo = Photo.objects.create(incident=incident, images=uploaded_file)

                messages.success(request, 'Le prolongement a été ajouté avec succès.')
            return redirect('utilisateur:declare_incident')
        else:
            print(form.errors)
    else:
        form = DemandeProlongementForm()
    return render(request, 'compte_conducteur.html', {'form': form})
