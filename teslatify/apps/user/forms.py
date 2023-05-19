from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User

custom_errors_msg = {
    'required': 'Pflichtfeld',
    'invalid': _('Eingabe nicht gültig')
}


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email')

