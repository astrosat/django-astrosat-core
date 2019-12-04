"""
Django settings for example project.

Generated by 'django-admin startproject' using Django 2.2.
"""

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

import environ
import os

from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from astrosat.utils import DynamicSetting

env = environ.Env()

PROJECT_NAME = "Example Project"
PROJECT_SLUG = slugify(PROJECT_NAME)
PROJECT_EMAIL = "{role}@astrosat.space"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "shhh..."

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # api...
    "rest_framework",
    "drf_yasg",
    # astrosat...
    "astrosat",
    # this app...
    "example",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # I override some built-in templates (rest_framework, allauth, & rest_auth)
            # in order for this to work, I need to make sure that the following directories are checked
            # before their default locations (see the comment in "loaders" for more info)
            os.path.join(BASE_DIR, "example/templates/")
        ],
        # 'APP_DIRS': True,
        "OPTIONS": {
            "loaders": [
                # first look at files in DIR, then look in the standard place for each INSTALLED_APP
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "example.wsgi.application"


# Migrations
# hard coded migration to set sites table
MIGRATION_MODULES = {"sites": "example.contrib.sites.migrations"}

SITE_ID = 1

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Emailing

# (don't really send email in this example project...)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# (...and don't really send it to/from these people...)
ADMINS = [(PROJECT_NAME, PROJECT_EMAIL.format(role="noreply"))]
MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = f"{PROJECT_NAME} <{PROJECT_EMAIL.format(role='noreply')}>"

# Internationalization

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [("en-us", _("American English")), ("en-gb", _("British English"))]

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# API

REST_FRAMEWORK = {

}

SWAGGER_SETTINGS = {
    "DOC_EXPANSION": "none",
    "OPERATIONS_SORTER": None,
    "TAGS_SORTER": "alpha",
    "DEFAULT_MODEL_RENDERING": "example",
}

# Profiling

if DEBUG:

    # see "https://gist.github.com/douglasmiranda/9de51aaba14543851ca3"
    # for more tips about making django_debug_toolbar to play nicely w/ Docker

    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

    INSTALLED_APPS += ["debug_toolbar", "pympler"]  # noqa F405
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "astrosat.middleware.JSONDebugToolbarMiddleware",
    ]  # noqa F405
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TEMPLATE_CONTEXT": True, "SHOW_COLLAPSED": True}
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
        # TODO: THIS WILL NOT WORK B/C OF https://github.com/pympler/pympler/pull/99
        # TODO: IN THE MEANTIME I'VE WRITTEN MY OWN DECORATOR THAT ACCOMPLISHES THE SAME THING
        # 'pympler.panels.MemoryPanel',
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]

# astrosat-specific stuff...

AWS_BUCKET_NAME = env("DJANGO_AWS_BUCKET_NAME", default="default-bucket")
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID", default="default-access-key-id")
AWS_SECRET_ACCESS_KEY = env(
    "DJANGO_AWS_SECRET_ACCESS_KEY", default="default-secret-access-key"
)
