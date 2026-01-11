from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from ldap3 import MODIFY_ADD, MODIFY_DELETE

from ..models import Mastodon
from ...accounts.models import User
from ...settings import LDAP_MASTODON_KEY, LDAP_MASTODON_OBJECT_CLASS


@receiver(m2m_changed, sender=Mastodon.users.through)
def sync_user_change_to_ldap(sender, instance, action, pk_set, **kwargs):
    """
    Sync user changes to LDAP
    """
    conn = settings.LDAP_CONNECTION

    user_dns = list(User.objects.filter(pk__in=pk_set).distinct().values_list('object_dn', flat=True))

    if action == "post_add":
        for user in user_dns:
            conn.bind()
            conn.modify(user, {
                'objectClass': [(MODIFY_ADD, [LDAP_MASTODON_OBJECT_CLASS, ])],
            })
            conn.unbind()

            conn.bind()
            conn.modify(user, {
                LDAP_MASTODON_KEY: [(MODIFY_ADD, [instance.name, ])]
            })


    if action == "post_remove":
        for user in user_dns:
            conn.bind()
            conn.modify(user, {
                LDAP_MASTODON_KEY: [(MODIFY_DELETE, [instance.name, ])]
            })

    conn.unbind()