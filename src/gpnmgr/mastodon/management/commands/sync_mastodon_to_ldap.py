from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _
from ldap3 import MODIFY_ADD

from gpnmgr.mastodon.models import Mastodon
from gpnmgr.settings import LDAP_MASTODON_KEY, LDAP_MASTODON_OBJECT_CLASS


class Command(BaseCommand):
    help = 'Write mastodon account users to LDAP'

    def handle(self, *args, **options):
        mastodon_accounts = Mastodon.objects.all()
        conn = settings.LDAP_CONNECTION

        for mastodon_account in mastodon_accounts:
            print(_('Syncing users of %(account)s to LDAP') % {
                'account': mastodon_account.name
            })

            for user in mastodon_account.users.all():
                print(_('Adding user %(user)s') % {
                    'user': user
                })
                conn.bind()
                conn.modify(user.object_dn, {
                    'objectClass': [(MODIFY_ADD, [LDAP_MASTODON_OBJECT_CLASS, ])],
                })
                conn.unbind()

                conn.bind()
                conn.modify(user.object_dn, {
                    LDAP_MASTODON_KEY: [(MODIFY_ADD, [mastodon_account.name, ])]
                })