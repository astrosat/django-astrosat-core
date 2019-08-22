import environ

from django.conf import settings

from astrosat.utils import DynamicSetting


env = environ.Env()


AWS_BUCKET_NAME = getattr(settings, "AWS_BUCKET_NAME",  None)

AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID",  None)

AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY",  None)

# MY_TEST_SETTING = getattr(
#     settings, "MY_TEST_SETTING",
#     DynamicSetting(
#         "astrosat.AstrosatSettings.my_test_setting",
#         env("DJANGO_MY_TEST_SETTING", default=False)
#     )
# )
