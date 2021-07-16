from rest_framework.routers import DefaultRouter, SimpleRouter

# Most clients append a slash to their requests.
# Some older ones (edge) do not, or do this inconsistently.
# DRF can handle this via the `trailing_slash` kwarg
# (as per https://www.django-rest-framework.org/api-guide/routers/#api-guide)
# However, this means that requests must use ALL or NONE trailing_slashes
# The two classes below use clever regexes to cater for BOTH cases;
# They should be used in app's "urls.py" whenever trailing_slashes might be an issue


class SlashlessDefaultRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        self.trailing_slash = '/?'
        super().__init__(*args, **kwargs)


class SlashlessSimpleRouter(SimpleRouter):
    def __init__(self, *args, **kwargs):
        self.trailing_slash = '/?'
        super().__init__(*args, **kwargs)
