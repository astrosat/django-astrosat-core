import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from astrosat.mixins import SingletonMixin


class AstrosatSettings(SingletonMixin, models.Model):
    class Meta:
        verbose_name = "Astrosat Settings"
        verbose_name_plural = "Astrosat Settings"

    # my_test_setting = models.BooleanField(default=False)

    def __str__(self):
        return "Astrosat Settings"


class DatabaseLogRecord(models.Model):

    """
    model used by astrosat.utils.db_log_handler to log records to the db
    """

    class Meta:
        verbose_name = "Log Record"
        verbose_name_plural = "Log Records"
        ordering = ("-created",)

    LevelChoices = (
        (logging.NOTSET, _('NotSet')),
        (logging.INFO, _('Info')),
        (logging.WARNING, _('Warning')),
        (logging.DEBUG, _('Debug')),
        (logging.ERROR, _('Error')),
        (logging.FATAL, _('Fatal')),
    )

    created = models.DateTimeField(auto_now_add=True)
    logger_name = models.CharField(max_length=128)
    level = models.PositiveIntegerField(choices=LevelChoices, default=logging.ERROR)
    message = models.TextField()
    trace = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.message
