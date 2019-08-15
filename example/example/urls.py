from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView

from astrosat.urls import urlpatterns as astrosat_urlpatterns


admin.site.site_header = "Admin for Example Project for Astrosat Apps"

urlpatterns = [
    # admin...
    path('admin/', admin.site.urls),

    # api...
    # TODO

    # astrosat...
    path('astrosat/', include(astrosat_urlpatterns)),

    # index...
    path('', TemplateView.as_view(template_name="example/index.html"))

]


if "debug_toolbar" in settings.INSTALLED_APPS:

    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns
