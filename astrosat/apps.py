from django.apps import AppConfig

from . import APP_NAME
from .utils import DynamicSetting


class AstrosatConfig(AppConfig):

    name = APP_NAME
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):

        try:
            # register any checks...
            import astrosat.checks  # noqa
        except ImportError:
            pass

        try:
            # register any signals...
            import astrosat.signals  # noqa
        except ImportError:
            pass

        # update how django.conf.settings works, by letting variables
        # defined there be instances of the DynamicSetting class
        DynamicSetting.configure()
