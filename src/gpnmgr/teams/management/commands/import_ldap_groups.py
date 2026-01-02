from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _
from ldap3 import SUBTREE

from gpnmgr.accounts.models import User
from gpnmgr.settings import LDAP_GROUP_MEMBER_KEY, LDAP_GROUP_MANAGER_KEY, LDAP_GROUP_PK, LDAP_USER_PK
from gpnmgr.teams.models import Team


class Command(BaseCommand):
    help = 'Read groups from LDAP and map users'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Don\'t write any changes')

    def handle(self, *args, dry_run, **options):
        if dry_run:
            print('DRY RUN')
        conn = settings.LDAP_CONNECTION
        conn.bind()

        conn.search(
            search_base=f'{settings.LDAP_GROUP_OU},{settings.LDAP_BASE_DN}',
            search_filter=f'(objectClass={settings.LDAP_GROUP_OBJECT_CLASS})',
            search_scope=SUBTREE,
            attributes=[
                LDAP_GROUP_PK,
                LDAP_GROUP_MEMBER_KEY,
                LDAP_GROUP_MANAGER_KEY
            ],
        )

        entries = conn.entries
        print(f"Found {len(entries)} group entries in LDAP.")

        for entry in entries:
            attrs = entry.entry_attributes_as_dict

            group_name = attrs.get(LDAP_GROUP_PK, [])[0]
            members = attrs.get(LDAP_GROUP_MEMBER_KEY, [])
            owners = attrs.get(LDAP_GROUP_MANAGER_KEY, [])

            print(_('Handling group %(group)s') % {
                'group': group_name
            })

            if not dry_run:
                team, created = Team.objects.get_or_create(ldap_name=group_name)
                if created:
                    team.slug = group_name
                    team.name = group_name
                    team.save()
                    print(_('Created team'))
            else:
                team = Team.objects.filter(ldap_name=group_name).first()
                if team is None:
                    print(_('Team not existing, would create'))

            print(_('Syncing'))

            ldap_group_members = [User.objects.get(username=member.split(',')[0].split('=')[1]) for member in members if LDAP_USER_PK in member]
            ldap_group_owners = [User.objects.get(username=owner.split(',')[0].split('=')[1]) for owner in owners if LDAP_USER_PK in owner]
            if not dry_run:
                team.members.set(ldap_group_members)
                team.admins.set(ldap_group_owners)
                team.save()

            print(f'Add {len(ldap_group_members)} members to team: {team}')
            print(f'Added {len(ldap_group_owners)} managers to team: {team}')

        conn.unbind()
        print("Import complete.")