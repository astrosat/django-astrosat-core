from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

# from core.utils import DynamicSetting


TEST_SETTING = getattr(settings, 'ASTROSAT_TEST_SETTING', None)

AWS_BUCKET_NAME = getattr(settings, "AWS_BUCKET_NAME",  None)
AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID",  None)
AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY",  None)
