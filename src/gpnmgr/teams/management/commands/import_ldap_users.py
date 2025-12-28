from django.conf import settings
from django.core.management import BaseCommand
from ldap3 import SUBTREE

from gpnmgr.accounts.models import User
from gpnmgr.settings import LDAP_USER_PK


class Command(BaseCommand):
    help = 'Read users from LDAP and populate user database'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Don\'t write any changes')

    def handle(self, *args, dry_run, **options):
        if dry_run:
            print('DRY RUN')

        conn = settings.LDAP_CONNECTION

        conn.search(
            search_base=f'{settings.LDAP_USER_OU},{settings.LDAP_BASE_DN}',
            search_filter=f'(objectClass={settings.LDAP_USER_OBJECT_CLASS})',
            search_scope=SUBTREE,
            attributes=[
                'sn',
                LDAP_USER_PK,
            ],
        )

        entries = conn.entries
        print(f'Found {len(entries)} users entries in LDAP.')

        for entry in entries:
            attrs = entry.entry_attributes_as_dict

            username = attrs.get(LDAP_USER_PK, [None])[0]
            last_name = attrs.get('sn', [None])[0]

            if not username:
                print(f'Skipping entry without {LDAP_USER_PK}: {entry.entry_dn}')
                continue

            if dry_run:
                if User.objects.filter(username=username).count() > 0:
                    print(f'User already exists: {username}')
                else:
                    print(f'Would create user: {username}')
            else:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'last_name': last_name or '',
                        'display_name': last_name or None,
                    },
                )

                if created:
                    user.set_unusable_password()
                    user.save()
                    print(f'Created new user: {username}')
                else:
                    user.last_name = last_name or ''
                    user.display_name = last_name or ''
                    user.save()
                    print(f'User already exists: {username}. Synced attributes')

        conn.unbind()
        print('Import complete.')