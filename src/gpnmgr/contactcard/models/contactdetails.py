from __future__ import annotations


from django.db import models
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from gpnmgr.accounts.models import User

class ContactDetails(User):

    @property
    def contact_details(self):
        return {_(settings.CONTACTCARD_FIELDS.get(field).get('display_name', field)): getattr(self, field) for field in settings.CONTACTCARD_FIELDS.keys()}

for field in settings.CONTACTCARD_FIELDS.keys():
    ContactDetails.add_to_class(field, models.CharField(max_length=255, blank=True, null=True, verbose_name=_(field)))
