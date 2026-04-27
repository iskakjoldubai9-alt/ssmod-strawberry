from django import forms
from django.contrib.auth.models import User


class SignUpForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=True, label="Телефон номер")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']  # Керектүү талаалар

    # Бул жерге кийин кошумча логика кошсоңуз болот