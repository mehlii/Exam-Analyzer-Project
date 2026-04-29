# accounts/views.py
# Türkçe not: Kayıt ol / giriş yap / çıkış yap akışı.

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

from .forms import RegisterForm


@csrf_protect
def register_view(request):
    # Türkçe not: Kullanıcı kaydolunca otomatik login olacak.
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})

