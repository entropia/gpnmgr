from __future__ import annotations

import datetime
import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from gpnmgr.accounts.models import User
from gpnmgr.teams.models import Team


class AccountRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    name = models.CharField(_("Name"), max_length=255, unique=False)
    email = models.EmailField(_("Email"), max_length=255, unique=False)
    invite_text = models.CharField(_("Invite text"), max_length=255, null=True, default=None)
    team = models.ForeignKey(Team, verbose_name=_("Team"), null=True, blank=True, on_delete=models.SET_NULL, related_name='member_invites')

    inviter = models.ForeignKey(User, verbose_name=_("Inviter"), null=True, blank=True, on_delete=models.SET_NULL, related_name='sent_invites')

    is_revoked = models.BooleanField(_("Revocation"), default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Account request")
        verbose_name_plural = _("Account requests")
        default_permissions = ()
        permissions = [
            ('manage_requests', 'May see and revoke requests'),
        ]

    def __str__(self) -> str:
        return f'Request for {self.name}'

    @property
    def is_valid(self) -> bool:
        if self.is_revoked:
            return False
        return self.created_at < (timezone.now() + datetime.timedelta(days=settings.USER_INVITE_TIMEOUT_DAYS)) and self.confirmed_at == None

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None

    def get_absolute_url(self) -> str:
        return reverse('user_confirm')
