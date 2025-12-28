from auditlog.registry import auditlog

from .team import Team

auditlog.register(Team, m2m_fields={'admins','members'})