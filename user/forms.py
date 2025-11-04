# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
from .models import Space

# LUOKAT
# ======

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Salasana', widget=forms.PasswordInput)
    phone = forms.CharField(label='Puhelin')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': 'Käyttäjätunnus',
            'first_name': 'Etunimi',
            'last_name': 'Sukunimi',
            'email': 'Sähköposti',
            'password': 'Salasana',
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        exclude = ['owner', 'slug']