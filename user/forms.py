from django import forms
from django.contrib.auth.models import User

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