import logging
import re

from astrosat.conf import app_settings as astrosat_settings


class RestrictLogsByNameFilter(logging.Filter):
    """
    Lets me selectively choose which modules are allowed to generate log records.
    Wrote this code b/c geopandas went a bit crazy with output.
    To use just subclass and set names_to_restrict and level_to_allow
    """

    names_to_restrict = None
    level_to_allow = logging.NOTSET

    def __init__(self, *args, **kwargs):
        if not (self.names_to_restrict and self.level_to_allow):
            raise NotImplementedError(
                f"{self} requires 'names_to_restrict' and 'level_to_allow' to be set"
            )
        self.names_to_restrict = re.compile(self.names_to_restrict)
        super().__init__(*args, **kwargs)

    def filter(self, record):
        if self.names_to_restrict.match(record.name):
            return record.levelno >= self.level_to_allow
        return True


class DatabaseLogHandler(logging.Handler):
    """
    sends a logging record to the db
    """

    default_formatter = logging.Formatter()

    def emit(self, record):

        if astrosat_settings.ASTROSAT_ENABLE_DB_LOGGING:

            from astrosat.models import DatabaseLogRecord, DatabaseLogTag

            trace = None
            if record.exc_info:
                trace = self.default_formatter.formatException(record.exc_info)

            tags = map(
                lambda x: x[0],
                [
                    DatabaseLogTag.objects.get_or_create(name=tag_name)
                    for tag_name in getattr(record, "tags", [])
                ],
            )

            db_record = DatabaseLogRecord.objects.create(
                logger_name=record.name,
                level=record.levelno,
                message=record.getMessage(),
                trace=trace,
            )
            db_record.tags.add(*tags)
