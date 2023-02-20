from django import forms as f
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class AuthForm(f.Form):
    username = f.CharField(label=_('User name'))
    password = f.CharField(widget=f.PasswordInput, label=_('Password'))


class RegisterForm(UserCreationForm):
    city = f.CharField(max_length=30, required=False, label=_('City'))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'city',)


class NamesEditForm(f.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    first_name = f.CharField(max_length=20, required=False, label=_('First name'))
    last_name = f.CharField(max_length=20, required=False, label=_('Last name'))
    email = f.EmailField(label='email', required=False)


class ReplenishmentForm(f.Form):
    amount = f.IntegerField(min_value=100, max_value=1e7, label=_('Amount'), help_text=_('rub.'))
