from django.shortcuts import render, redirect

from deplacement.forms import DeplacementForm


# Create your views here.
def enregistrer_deplacement(request):
    if request.method == 'POST':
        form = DeplacementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('deplacement:enregistrer_deplacement')
    else:
        form = DeplacementForm()

    return render(request, 'enregistrer_deplacement.html', {'form': form})
