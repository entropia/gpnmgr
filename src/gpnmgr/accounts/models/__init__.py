from auditlog.registry import auditlog

from .user import BaseUser, User
from .request import AccountRequest

auditlog.register(AccountRequest)