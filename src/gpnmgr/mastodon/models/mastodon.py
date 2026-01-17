from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models import User


class Mastodon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.CharField(_("Description"), max_length=255, null=True, default=None)

    users = models.ManyToManyField(User, verbose_name=_("Users"), related_name='mastodon', default=None)


    class Meta:
        ordering = ["name"]
        verbose_name = _("Mastodon account")
        verbose_name_plural = _("Mastodon accounts")
        default_permissions = ()
        permissions = [
            ('manage_accounts', 'May create, modify and delete accounts'),
        ]

    def __str__(self) -> str:
        return f'@{self.name}{settings.MASTODON_BASE}'

    @property
    def user_count(self) -> int:
        return self.users.count()
