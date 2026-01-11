from django.apps import AppConfig


class MastodonConfig(AppConfig):
    name = 'gpnmgr.mastodon'

    def ready(self):
        from . import signals