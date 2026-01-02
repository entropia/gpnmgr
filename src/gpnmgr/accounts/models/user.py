from __future__ import annotations

from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from gpnmgr import settings


class BaseUser(AbstractUser):
    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return self.display

    @property
    def display(self) -> str:
        if hasattr(self, 'user'):
            return self.user.display
        return self.get_full_name()

class User(BaseUser):
    display_name = models.CharField(max_length=150, verbose_name=_('Display name'), null=True, blank=True)
    object_dn = models.CharField(max_length=150, verbose_name=_('LDAP DN'), null=True, blank=True)

    class Meta:
        default_permissions = ()
        ordering = ['username']

    def __str__(self):
        return self.display

    @property
    def display(self) -> str:
        if self.display_name is None:
            return self.get_full_name()
        if self.display_name.lower() != self.username.lower():
            return f'{self.display_name} ({self.username})'
        return self.display_name

    def get_absolute_url(self) -> str:
        return reverse('user_profile')

    def has_perm(self, perm: str, obj: Optional[Model] = None) -> bool:
        if not self.is_active:
            return False
        for group in self.groups.all():
            try:
                if perm in settings.permissions[group.name]:
                    return True
            except KeyError:
                pass
        return False

    # Is no used
    def has_module_perms(self, app_label: str) -> bool:
        return False
