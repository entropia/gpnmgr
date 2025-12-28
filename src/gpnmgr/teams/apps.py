from django.apps import AppConfig


class TeamsConfig(AppConfig):
    name = 'gpnmgr.teams'

    def ready(self):
        from . import signals