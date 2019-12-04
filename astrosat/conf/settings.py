import environ

from django.conf import settings

from astrosat.utils import DynamicSetting


env = environ.Env()


AWS_BUCKET_NAME = getattr(settings, "AWS_BUCKET_NAME", None)

AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID", None)

AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)


# required third party settings...
# (most of these are checked in checks.py)

REST_FRAMEWORK_SETTINGS = {

}

SWAGGER_SETTINGS = {

}
