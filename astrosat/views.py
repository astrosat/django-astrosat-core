from django.conf import settings
from django.http.response import StreamingHttpResponse
from django.urls import re_path
from django.views import defaults as default_views

from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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


api_schema_view = get_schema_view(
    openapi.Info(title="Django-Astrosat-Users API", default_version="v1"),
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
# proxies #
###########


class ProxyS3View(APIView):
    """
    View to retrieve object contents from S3 w/out exposing credentials to the client
    """

    permission_classes = [IsAuthenticated]

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
