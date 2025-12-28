from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from gpnmgr.accounts.models import User


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    object: User
    save_path_in_session = True
    title = _('My account')

    def get_object(self, queryset=None) -> User | AnonymousUser:
        return self.request.user
