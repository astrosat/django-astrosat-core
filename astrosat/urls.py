from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import DatabaseLogRecordViewSet, feature_tracking, ProxyS3View

##############
# API routes #
##############

api_router = SimpleRouter()
api_router.register(r"logs", DatabaseLogRecordViewSet)
api_urlpatterns = [
    path("", include(api_router.urls)),
    path("logs/tracking", feature_tracking, name="log-tracking"),
    path("proxy/s3", ProxyS3View.as_view(), name="proxy-s3"),
]

#################
# normal routes #
#################

urlpatterns = []
