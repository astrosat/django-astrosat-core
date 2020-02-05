from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http.response import StreamingHttpResponse
from django.urls import re_path
from django.views import defaults as default_views

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.serializers import CurrentUserDefault
from rest_framework.views import APIView

from django_filters import Filter
from django_filters.constants import EMPTY_VALUES

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view

from .utils import DataClient


###########
# swagger #
###########


class IsAdminOrDebug(BasePermission):
    def has_object_permission(self, request, view, obj):
        # allow swagger access to anybody in DEBUG mode
        # and only to the admin in all other cases
        user = request.user
        return user.is_superuser or settings.DEBUG


API_SCHEMA_TILE = f"{getattr(settings, 'PROJECT_NAME', 'Django-Astrosat')} API"

api_schema_view = get_schema_view(
    openapi.Info(title=API_SCHEMA_TILE, default_version="v1"),
    public=True,
    permission_classes=(IsAdminOrDebug,),
)

api_schema_views = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        api_schema_view.without_ui(cache_timeout=0),
        name="swagger-json",
    ),
    re_path(
        r"^swagger/$",
        api_schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger",
    ),
    re_path(
        r"^redoc/$",
        api_schema_view.with_ui("redoc", cache_timeout=0),
        name="swagger-redoc",
    ),
]


def swagger_current_user_default(serializer_field=None):
    # despite https://github.com/axnsan12/drf-yasg/commit/f81795d7454d9b1eb88874014ffd70b26289f905,
    # yasg still doesn't play nicely w/ CurrentUserDefault;
    # it doesn't pass 'serializer_field' to default()
    if serializer_field is not None:
        return CurrentUserDefault(serializer_field)
    return None


##################
# error handling #
##################

"""
To use these in a project simply add the following code to ROOT_URLCONF:
>handler400 = "astrosat.views.handler400"
>handler403 = "astrosat.views.handler403"
>handler404 = "astrosat.views.handler404"
>handler500 = "astrosat.views.handler400"
"""


def handler400(request, *args, **kwargs):
    defaults = {"template_name": "astrosat/400.html"}
    defaults.update(kwargs)
    return default_views.bad_request(request, *args, **defaults)


def handler403(request, *args, **kwargs):
    defaults = {"template_name": "astrosat/403.html"}
    defaults.update(kwargs)
    return default_views.permission_denied(request, *args, **defaults)


def handler404(request, *args, **kwargs):
    defaults = {"template_name": "astrosat/404.html"}
    defaults.update(kwargs)
    return default_views.page_not_found(request, *args, **defaults)


def handler500(request, *args, **kwargs):
    defaults = {"template_name": "astrosat/500.html"}
    defaults.update(kwargs)
    return default_views.server_error(request, *args, **defaults)


###########
# filters #
###########

class BetterBooleanFilterField(forms.CharField):
    """
    Converts valid input into boolean values to be used
    w/ BetterBooleanFilter below.
    """

    TRUE_VALUES = ["true", "yes", "1"]
    FALSE_VALUES = ["false", "no", "0"]

    def clean(self, value):
        value = self.to_python(value).casefold()
        if value in EMPTY_VALUES:
            value = None
        elif value in self.TRUE_VALUES:
            value = True
        elif value in self.FALSE_VALUES:
            value = False
        else:
            msg = f"'{value}' must be one of: {', '.join(self.TRUE_VALUES + self.FALSE_VALUES)}"
            raise ValidationError(msg)
        return value


class BetterBooleanFilter(Filter):
    """
    A more user-friendly boolean filter to accept more than just "True" and "False".
    It does this by using a CharField (BetterBooleanFilterField) instead of the default NullBooleanField.
    """

    field_class = BetterBooleanFilterField


###########
# proxies #
###########


class ProxyS3View(APIView):
    """
    View to retrieve object contents from S3 w/out exposing credentials to the client
    """

    permission_classes = [IsAuthenticated]

    _key_parameter = openapi.Parameter(
        "key",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Pathname of the bucket object to retrieve.",
    )

    @swagger_auto_schema(manual_parameters=[_key_parameter], responses={status.HTTP_200_OK: "StreamingHttpResponse"})
    def get(self, request):
        key = request.query_params.get("key")
        client = DataClient()
        obj = client.get_object(key)
        if obj:
            # client returns an instance of `botocore.response.StreamingBody`
            # (in case the data is very big); so I wrap it in a StreamingHttpResponse here
            return StreamingHttpResponse(obj)
        else:
            msg = f"Unable to retrieve object at '{key}'"
            raise APIException(msg)
