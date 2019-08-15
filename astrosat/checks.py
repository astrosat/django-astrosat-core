import pkg_resources  # pkg_resources is a more reliable way to check modules & versions

from django.conf import settings
from django.core.checks import register, Error, Tags

from . import APP_NAME


# apps required by astrosat
APP_DEPENDENCIES = [
    'rest_framework',
    'rest_framework_swagger',
]


@register(Tags.compatibility)
def check_dependencies(app_configs, **kwargs):
    """
    Makes sure that all django app dependencies are met.
    (Standard python dependencies are handled in setup.py.)
    Called by `AppConfig.ready()`.
    """

    # if not app_configs:
    #     from django.apps import apps
    #     app_configs = apps.get_app_configs()

    errors = []
    for i, dependency in enumerate(APP_DEPENDENCIES):
        if dependency not in settings.INSTALLED_APPS:
        # if dependency not in map(lambda app_config: app_config.label, app_configs):
            errors.append(
                Error(
                    f"You are using {APP_NAME} which requires the {dependency} module.  Please install it and add it to INSTALLED_APPS.",
                    id=f"{APP_NAME}:E{i:03}",
                )
            )

    return errors

@register(Tags.compatibility)
def check_api_settings(app_configs):

    errors = []

    api_package = pkg_resources.get_distribution("djangorestframework")
    if pkg_resources.parse_version(api_package.version) > pkg_resources.parse_version("3.9.4"):

        # the jump from DRF 3.9 to 3.10 broke lots of stuff
        # to continue to use swagger w/ DRF you must explicitly not use the OpenAPI schemas
        # (as per https://www.django-rest-framework.org/community/3.10-announcement/#continuing-to-use-coreapi)

        if settings.REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] != "rest_framework.schemas.coreapi.AutoSchema":
            errors.append(
                Error(
                    f"You are using 'rest_framework_swagger' which requires REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] to be set to 'rest_framework.schemas.coreapi.AutoSchema'."
                )
            )

    return errors
