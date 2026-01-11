from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.forms.widgets import TextInput, HiddenInput
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models import User
from gpnmgr.mastodon.models import Mastodon


class MastodonUserAddForm(ModelForm):
    user_input = CharField(required=False)

    class Meta:
        model = Mastodon
        fields = ('users', 'user_input')
        widgets = {
            'user_input': TextInput(attrs={'placeholder': _('Enter users to add'), 'autocomplete': 'off', 'aria-expanded': 'false', 'data-bs-toggle': 'dropdown', 'class': 'form-control dropdown-toggle', }),
            'users': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            initial['users'] = ''

        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        self.errors.pop('users')
        users = list(self.instance.users.all())

        invalid_users = []
        for user in self.data.get('users', []).split(','):
            new_user = User.objects.filter(username__iexact=user).first()
            if new_user is None:
                invalid_users.append(user)
                continue
            users.append(new_user)

        cleaned_data['users'] = users

        if len(invalid_users) > 0:
            raise ValidationError(_('The provided usernames %(invalid_users)s are invalid.' % {
                'invalid_users': ', '.join(invalid_users),
            }))

        return cleaned_data