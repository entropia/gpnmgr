from .settings import OAUTH_TEAM_MANAGER_GROUP
from .settings import OAUTH_FEDI_MANAGER_GROUP
from .settings import OAUTH_ADMIN_GROUP


team_manager_permissions = [
    'teams.manage_teams',
]

fedi_manager_permissions = [
    'fedi.manage_accounts',
]

admin_permissions = [
    'log.view_log'
]

permissions = {
    OAUTH_TEAM_MANAGER_GROUP: team_manager_permissions,
    OAUTH_FEDI_MANAGER_GROUP: fedi_manager_permissions,
    OAUTH_ADMIN_GROUP: team_manager_permissions + fedi_manager_permissions + admin_permissions,
}
