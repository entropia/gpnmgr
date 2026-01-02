from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.forms.widgets import TextInput, HiddenInput
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models import User
from gpnmgr.teams.models import Team


class TeamMemberAddForm(ModelForm):
    member_input = CharField(required=False)

    class Meta:
        model = Team
        fields = ('members', 'member_input')
        widgets = {
            'member_input': TextInput(attrs={'placeholder': _('Enter users to add'), 'autocomplete': 'off', 'aria-expanded': 'false', 'data-bs-toggle': 'dropdown', 'class': 'form-control dropdown-toggle', }),
            'members': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            initial['members'] = ''

        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        self.errors.pop('members')
        members = list(self.instance.members.all())

        invalid_users = []
        for member in self.data.get('members', []).split(','):
            new_user = User.objects.filter(username__iexact=member).first()
            if new_user is None:
                invalid_users.append(member)
                continue
            members.append(new_user)

        cleaned_data['members'] = members

        if len(invalid_users) > 0:
            raise ValidationError(_('The provided usernames %(invalid_users)s are invalid.' % {
                'invalid_users': ', '.join(invalid_users),
            }))

        return cleaned_data