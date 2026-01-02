from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models import User


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(_("Name"), max_length=255)
    slug = models.CharField(_("Abbreviation"), max_length=255, unique=True)
    cost_center = models.CharField(_("Cost Center"), max_length=255, default=None, null=True)
    primary_contact = models.CharField(_("Primary contact"), max_length=255, default=None, null=True)

    ldap_name = models.CharField(_("LDAP Name"), max_length=255, default=None, null=True, unique=True)

    admins = models.ManyToManyField(User, verbose_name=_("Administrators"), default=None)
    members = models.ManyToManyField(User, verbose_name=_("Members"), related_name='teams', default=None)


    class Meta:
        ordering = ["slug"]
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        default_permissions = ()
        permissions = [
            ('manage_teams', 'May create, modify and delete teams'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.slug})'

    @property
    def valid_members(self) -> QuerySet:
        # Members that are not placeholder
        return self.members.exclude(object_dn=settings.LDAP_PLACEHOLDER_DN)

    @property
    def valid_admins(self) -> QuerySet:
        # Admins that are not placeholder
        return self.admins.exclude(object_dn=settings.LDAP_PLACEHOLDER_DN)

    @property
    def non_admins(self) -> QuerySet:
        return self.valid_members.exclude(id__in=self.valid_admins.values_list('id', flat=True))

    @property
    def member_count(self) -> int:
        return self.valid_members.count()

    @property
    def admin_count(self) -> int:
        return self.valid_admins.count()