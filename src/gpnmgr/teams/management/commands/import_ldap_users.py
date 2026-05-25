from django.conf import settings
from django.core.management import BaseCommand
from ldap3 import SUBTREE

from gpnmgr.accounts.models import User

from gpnmgr.settings import LDAP_USER_PK, LDAP_USER_MAIL_PK


class Command(BaseCommand):
    help = 'Read users from LDAP and populate user database'
    sync_contactcard = False

    def __init__(self, *args, **kwargs):
        from django.apps import apps
        if apps.is_installed('gpnmgr.contactcard'):
            self.sync_contactcard = True
            self.contactcard_attrs = [str(key) for key in settings.CONTACTCARD_FIELDS.keys()]

        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Don\'t write any changes')

    def handle(self, *args, dry_run, **options):
        if dry_run:
            print('DRY RUN')

        attributes = [
            'sn',
            LDAP_USER_MAIL_PK,
            LDAP_USER_PK,
        ]

        if self.sync_contactcard:
            attributes += self.contactcard_attrs

        conn = settings.LDAP_CONNECTION
        conn.bind()

        conn.search(
            search_base=f'{settings.LDAP_USER_OU},{settings.LDAP_BASE_DN}',
            search_filter=f'(objectClass={settings.LDAP_USER_OBJECT_CLASS})',
            search_scope=SUBTREE,
            attributes=attributes,
        )

        entries = conn.entries
        print(f'Found {len(entries)} users entries in LDAP.')

        for entry in entries:
            attrs = entry.entry_attributes_as_dict

            username = attrs.get(LDAP_USER_PK, [None])[0]
            last_name = attrs.get('sn', [None])[0]
            email = None if len(attrs.get(LDAP_USER_MAIL_PK, [None])) == 0 else attrs.get(LDAP_USER_MAIL_PK, [None])[0]
            object_dn = entry.entry_dn

            if self.sync_contactcard:
                contactcard = {}
                for attr in self.contactcard_attrs:
                    if settings.CONTACTCARD_FIELDS[attr]['is_list']:
                        contactcard[attr] = ', '.join([str(entry) for entry in attrs.get(attr, [])])
                    else:
                        contactcard[attr] = None if len(attrs.get(LDAP_USER_MAIL_PK, [None])) == 0 else attrs.get(LDAP_USER_MAIL_PK, [None])[0] or ''

            if not username:
                print(f'Skipping entry without {LDAP_USER_PK}: {entry.entry_dn}')
                continue

            if dry_run:
                if User.objects.filter(username=username).count() > 0:
                    print(f'User already exists: {username}')
                else:
                    print(f'Would create user: {username}')
            else:
                defaults = {
                    'last_name': last_name or '',
                    'display_name': last_name or None,
                    'email': email or None,
                    'object_dn': object_dn,
                }

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults=defaults,
                )

                if created:
                    user.set_unusable_password()
                    user.save()
                    print(f'Created new user: {username}')
                else:
                    user.last_name = last_name or ''
                    user.display_name = last_name or ''
                    user.email = email or ''
                    user.object_dn = object_dn
                    user.save()
                    print(f'User already exists: {username}. Synced attributes')

                if self.sync_contactcard:
                    from gpnmgr.contactcard.models import ContactDetails
                    ContactDetails(pk=user.pk, **contactcard).save_base(raw=True)
                    print(f'Synced contactcard for user: {username}')

        conn.unbind()
        print('Import complete.')
