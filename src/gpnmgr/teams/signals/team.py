from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from ldap3 import SUBTREE, MODIFY_ADD, MODIFY_DELETE

from ..models import Team
from ...accounts.models import User
from ...settings import LDAP_GROUP_MEMBER_KEY, LDAP_GROUP_MANAGER_KEY, LDAP_PLACEHOLDER_DN, LDAP_GROUP_MEMBER_REQUIRED


@receiver(m2m_changed, sender=Team.admins.through)
def ensure_admin_is_member(sender, instance, action, pk_set, **kwargs):
    """
    Ensure that all admins are also members of the team.
    """
    if action == "pre_add":
        non_members = pk_set - set(instance.members.values_list("pk", flat=True))
        if non_members:
            raise ValidationError(
                "All admins must also be members of the team."
            )

@receiver(m2m_changed, sender=Team.members.through)
def sync_member_change_to_ldap(sender, instance, action, pk_set, **kwargs):
    """
    Sync member changes to LDAP
    """
    conn = settings.LDAP_CONNECTION
    conn.bind()
    conn.search(
        search_base=f'{settings.LDAP_GROUP_OU},{settings.LDAP_BASE_DN}',
        search_filter=f'(&(objectClass={settings.LDAP_GROUP_OBJECT_CLASS})(cn={instance.ldap_name}))',
        search_scope=SUBTREE,
        attributes=[
            LDAP_GROUP_MEMBER_KEY
        ],
    )

    group_entries = conn.entries

    if len(group_entries) == 0:
        raise IntegrityError(
            f'There is no group found in LDAP with the name {instance.ldap_name}'
        )

    group_dn = group_entries[0].entry_dn

    user_dns = list(User.objects.filter(pk__in=pk_set).distinct().values_list('object_dn', flat=True))

    if action == "post_add":
        conn.modify(group_dn, {
            LDAP_GROUP_MEMBER_KEY: [(MODIFY_ADD, user_dns)]
        })


    if action == "post_remove":
        if instance.valid_members.count() == 0 and LDAP_GROUP_MEMBER_REQUIRED:
            instance.members.add(User.objects.get(object_dn=LDAP_PLACEHOLDER_DN))
            conn.bind()
        conn.modify(group_dn, {
            LDAP_GROUP_MEMBER_KEY: [(MODIFY_DELETE, user_dns)]
        })

    conn.unbind()

@receiver(m2m_changed, sender=Team.admins.through)
def sync_admin_change_to_ldap(sender, instance, action, pk_set, **kwargs):
    """
    Sync admin changes to LDAP
    """
    conn = settings.LDAP_CONNECTION
    conn.bind()
    conn.search(
        search_base=f'{settings.LDAP_GROUP_OU},{settings.LDAP_BASE_DN}',
        search_filter=f'(&(objectClass={settings.LDAP_GROUP_OBJECT_CLASS})(cn={instance.ldap_name}))',
        search_scope=SUBTREE,
        attributes=[
            LDAP_GROUP_MANAGER_KEY
        ],
    )

    group_entries = conn.entries

    if len(group_entries) == 0:
        raise IntegrityError(
            f'There is no group found in LDAP with the name {instance.ldap_name}'
        )

    group_dn = group_entries[0].entry_dn

    user_dns = list(User.objects.filter(pk__in=pk_set).distinct().values_list('object_dn', flat=True))

    if action == "post_add":
        conn.modify(group_dn, {
            LDAP_GROUP_MANAGER_KEY: [(MODIFY_ADD, user_dns)]
        })

    if action == "post_remove":
        conn.modify(group_dn, {
            LDAP_GROUP_MANAGER_KEY: [(MODIFY_DELETE, user_dns)]
        })

    conn.unbind()