from django.urls import include, path

from .routers import SlashlessSimpleRouter
from .views import DatabaseLogRecordViewSet, create_log_records, ProxyS3View

##############
# API routes #
##############

api_router = SlashlessSimpleRouter()
api_router.register(r"logs", DatabaseLogRecordViewSet)
api_urlpatterns = [
    path("", include(api_router.urls)),
    path("logs/tracking", create_log_records, name="log-tracking"),
    path("proxy/s3", ProxyS3View.as_view(), name="proxy-s3"),
]

#################
# normal routes #
#################

urlpatterns = []
