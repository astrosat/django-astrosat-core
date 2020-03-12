import logging
import re


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

        from astrosat.models import DatabaseLogRecord


        trace = None
        if record.exc_info:
            trace = self.default_formatter.formatException(record.exc_info)

        DatabaseLogRecord.objects.create(
            logger_name=record.name,
            level=record.levelno,
            message=record.getMessage(),
            trace=trace,
        )
