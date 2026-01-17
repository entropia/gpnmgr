from django.core.exceptions import ValidationError
from django.forms import Form, EmailField
from django.forms.fields import CharField
from django.forms.widgets import TextInput, PasswordInput
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models import User


class AccountRequestConfirmForm(Form):
    username = CharField(required=True)
    display_name = CharField(required=True)
    email = EmailField(disabled=True)
    password = CharField(required=True, widget=PasswordInput)
    password_confirm = CharField(required=True, widget=PasswordInput)

    class Meta:
        fields = ('username', 'display_name', 'email', 'password', 'password_confirm')
        widgets = {
            'username': TextInput(attrs={'placeholder': _('Enter users to add'), 'autocomplete': 'off', }),
            'display_name': TextInput(attrs={'placeholder': _('Enter users to add'), 'autocomplete': 'off', }),
        }

    def clean_username(self):
        if User.objects.filter(username__iexact=self.data.get('username')).count() > 0:
            raise ValidationError(_('The username is already taken.'))
        return self.data.get('username')

    def clean_password(self):
        if self.data.get('password') != self.data.get('password_confirm'):
            raise ValidationError(_('Passwords do not match.'))
        return self.data.get('password')