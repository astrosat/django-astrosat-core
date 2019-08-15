from django.urls import path

from rest_framework_swagger.views import get_swagger_view


swagger_view = get_swagger_view(title="ThermCERT API")

urlpatterns = [
    path('swagger/', swagger_view, name="astrosat-swagger"),
]
