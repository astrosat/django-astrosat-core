from django.db import models

from astrosat.mixins import SingletonMixin

class AstrosatSettings(SingletonMixin, models.Model):

    class Meta:
        verbose_name = "Astrosat Settings"
        verbose_name_plural = "Astrosat Settings"

    # my_test_setting = models.BooleanField(default=False)

    def __str__(self):
        return "Astrosat Settings"
