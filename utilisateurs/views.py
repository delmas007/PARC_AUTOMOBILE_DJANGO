from random import sample
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
from Model.models import Roles, Utilisateur, Vehicule, Photo
from utilisateurs.forms import ConducteurClientForm
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

            context['form'] = form
            return render(request, 'inscription_client.html', context=context)

    form = UserRegistrationForm()
    context['form'] = form
    return render(request, 'inscription_client.html', context=context)


class Connexion_user(LoginView):
    template_name = 'connexion_user.html'
    form_class = ConnexionForm

    def get_success_url(self) -> str:
        if self.request.user.roles.role == 'CLIENT':
            return reverse('utilisateur:Accueil_user')
        if self.request.user.roles.role == 'CONDUCTEUR':
            return reverse('utilisateur:Acceuil_conducteur')


def Acceuil_conducteur(request):
    return render(request, 'compte_conducteur.html')
