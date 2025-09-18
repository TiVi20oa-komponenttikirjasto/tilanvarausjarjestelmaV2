from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['idNumber', 'firstname', 'lastname', 'email', 'phone',]
        labels = {
            'idNumber': 'ID Numero',
            'firstname': 'Etunimi',
            'lastname': 'Sukunimi',
            'email': 'Sähköposti',
            'phone': 'Puhelin',
        }