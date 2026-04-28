# accounts/forms.py
# Türkçe not: Kayıt formu (Django'nun built-in auth sistemi).

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    # Türkçe not: İsterseniz e-posta alanını da zorunlu yapabiliriz.
    email = forms.EmailField(required=False, help_text="Opsiyonel")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

