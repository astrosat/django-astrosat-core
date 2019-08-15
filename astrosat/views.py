from django.http.response import StreamingHttpResponse
from django.views import defaults as default_views

from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .utils import DataClient


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
    defaults = {
        "template_name": "astrosat/400.html",
    }
    defaults.update(kwargs)
    return default_views.bad_request(request, *args, **defaults)


def handler403(request, *args, **kwargs):
    defaults = {
        "template_name": "astrosat/403.html",
    }
    defaults.update(kwargs)
    return default_views.permission_denied(request, *args, **defaults)

def handler404(request, *args, **kwargs):
    defaults = {
        "template_name": "astrosat/404.html",
    }
    defaults.update(kwargs)
    return default_views.page_not_found(request, *args, **defaults)

def handler500(request, *args, **kwargs):
    defaults = {
        "template_name": "astrosat/500.html",
    }
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
