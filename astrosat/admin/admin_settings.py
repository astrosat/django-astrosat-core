from django.contrib import admin
from astrosat.models import AstrosatSettings


@admin.register(AstrosatSettings)
class AstrosatSettingsAdmin(admin.ModelAdmin):
    pass
