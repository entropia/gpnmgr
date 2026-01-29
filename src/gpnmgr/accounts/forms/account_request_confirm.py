from django.core.exceptions import ValidationError
from django.forms import Form, EmailField
from django.forms.fields import CharField
from django.forms.widgets import TextInput, PasswordInput
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models import User


def validate_username(value):
    import re
    if re.match(r"^[a-zA-Z0-9._-]+$", value) is None:
        raise ValidationError(_('Username may only contain letters, numbers, dots, dashes and underscores.'))
    if len(value) < 3:
        raise ValidationError(_('Username must be at least 3 characters long.'))
    if value[0] in ['.', '_', '-'] or value[-1] in ['.', '_', '-']:
        raise ValidationError(_('Username may not start or end with a dot, dash or underscore.'))


class AccountRequestConfirmForm(Form):
    username = CharField(required=True, validators=[validate_username])
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