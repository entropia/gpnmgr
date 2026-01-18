#!/usr/bin/env sh

/usr/bin/env python manage.py import_ldap_users
/usr/bin/env python manage.py import_ldap_groups
/usr/bin/env python manage.py import_mastodon_accounts