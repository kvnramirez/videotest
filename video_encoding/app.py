from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class VideotestConfig(AppConfig):
    name = 'video_encoding'
    verbose_name = _('profiles')

    def ready(self):
        import signals  # noqa