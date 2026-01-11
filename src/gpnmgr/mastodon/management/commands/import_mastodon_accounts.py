from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _
from ldap3 import SUBTREE

from gpnmgr.accounts.models import User
from gpnmgr.mastodon.models import Mastodon
from gpnmgr.settings import LDAP_MASTODON_KEY


class Command(BaseCommand):
    help = 'Read mastodon accounts from LDAP and create objects'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Don\'t write any changes')

    def handle(self, *args, dry_run, **options):
        if dry_run:
            print('DRY RUN')
        conn = settings.LDAP_CONNECTION
        conn.bind()

        conn.search(
            search_base=f'{settings.LDAP_USER_OU},{settings.LDAP_BASE_DN}',
            search_filter=f'(objectClass={settings.LDAP_MASTODON_OBJECT_CLASS})',
            search_scope=SUBTREE,
            attributes=[
                LDAP_MASTODON_KEY,
            ],
        )

        entries = conn.entries
        print(f"Found {len(entries)} users with mastodon access in LDAP.")

        mastodon_accounts = []
        for entry in entries:
            attrs = entry.entry_attributes_as_dict

            accounts = attrs.get(LDAP_MASTODON_KEY, [])

            for account in accounts:
                if account not in mastodon_accounts:
                    mastodon_accounts.append(account.lower())

        mastodon_objects = []
        for mastodon_account in mastodon_accounts:
            if not dry_run:
                mastodon, created = Mastodon.objects.get_or_create(name=mastodon_account)
                if created:
                    print(_('Created account %(account)s') % {
                        'account': mastodon_account
                    })
                mastodon_objects.append(mastodon)

            else:
                mastodon_account = Mastodon.objects.filter(name=mastodon_account).first()
                if mastodon_account is None:
                    print(_('Account not existing, would create %(account)s') % {
                        'account': mastodon_account
                    })

        for mastodon_object in Mastodon.objects.all():
            print(_('Clean users of account %(mastodon)s') % {
                'mastodon': mastodon_object
            })
            mastodon_object.users.set([])
            mastodon_object.save()

        for entry in entries:

            user = User.objects.get(object_dn=entry.entry_dn)

            attrs = entry.entry_attributes_as_dict
            accounts = attrs.get(LDAP_MASTODON_KEY, [])
            for account in accounts:
                if not dry_run:
                    mastodon_account = Mastodon.objects.filter(name=account.lower()).first()
                    mastodon_account.users.add(user)
                    mastodon_account.save()
                print(_('Add %(user)s to account %(account)s') % {
                    'user': user,
                    'account': account
                })

        conn.unbind()
        print("Import complete.")