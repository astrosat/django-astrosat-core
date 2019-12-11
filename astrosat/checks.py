from itertools import chain

from django.conf import settings
from django.core.checks import register, Error, Tags

from . import APP_NAME
from .conf import app_settings

# apps required by astrosat
APP_DEPENDENCIES = [
    "rest_framework",
    "django_filters",
    "drf_yasg",
]


@register(Tags.compatibility)
def check_dependencies(app_configs, **kwargs):
    """
    Makes sure that all django app dependencies are met.
    (Standard python dependencies are handled in setup.py.)
    Called by `AppConfig.ready()`.
    """

    errors = []
    for i, dependency in enumerate(APP_DEPENDENCIES):
        if dependency not in settings.INSTALLED_APPS:
            errors.append(
                Error(
                    f"You are using {APP_NAME} which requires the {dependency} module.  Please install it and add it to INSTALLED_APPS.",
                    id=f"{APP_NAME}:E{i:03}",
                )
            )

    return errors


@register(Tags.compatibility)
def check_settings(app_configs):
    """
    Makes sure that some required settings are set as expected
    """

    errors = []

    # nothing to see here

    return errors


@register(Tags.compatibility)
def check_third_party_settings(app_configs):

    errors = []

    third_party_settings = [
        app_settings.REST_FRAMEWORK_SETTINGS,
        app_settings.SWAGGER_SETTINGS,
    ]

    for key, value in chain(*map(lambda  x: x.items(), third_party_settings)):
        setting = getattr(settings, key, None)
        if setting != value:
            errors.append(
                Error(
                    f"You are using {APP_NAME} which requires {key} to be set to {value}."
                )
            )
    return errors
