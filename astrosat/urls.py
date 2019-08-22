from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProxyS3View


##############
# API routes #
##############

api_router = SimpleRouter()
# (if I had apps that used ViewSets (instead of CBVs or fns), I would register them here)
api_urlpatterns = [
    path("", include(api_router.urls)),
    path("proxy/s3", ProxyS3View.as_view(), name="proxy-s3")
]


#################
# normal routes #
#################

urlpatterns = []
