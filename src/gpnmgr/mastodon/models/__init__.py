from auditlog.registry import auditlog

from .mastodon import Mastodon

auditlog.register(Mastodon, m2m_fields={'users'})