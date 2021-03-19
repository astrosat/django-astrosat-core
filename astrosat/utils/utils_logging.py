import logging
import re
import uuid
import json
from logstash.handler_tcp import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase

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
                    for tag_name in getattr(record, "tags", []) or []
                ],
            )

            id = getattr(record, 'uuid', uuid.uuid4())
            db_record = DatabaseLogRecord.objects.create(
                logger_name=record.name,
                level=record.levelno,
                message=record.getMessage(),
                uuid=id,
                trace=trace,
            )
            db_record.tags.add(*tags)


def format_elasticsearch_timestamp(time):
    "Renders a timestamp in the format expected by elasticsearch"
    return LogstashFormatterBase.format_timestamp(time)


class ElasticsearchDocumentLogFormatter(LogstashFormatterBase):
    """
    Formats a json log record with additional fields needed for elasticsearch.
    Input records MUST be JSON.
    Based on LogstashFormatterBase/Version1 from python-logstash
    https://github.com/vklochan/python-logstash/blob/master/logstash/formatter.py
    """

    def __init__(self, constant_fields=dict()):
        self.constant_fields = constant_fields

    def format(self, record):

        record_fields = json.loads(record.getMessage())

        meta_fields = {
            "@timestamp": format_elasticsearch_timestamp(record.created),
            "@version": 1,
        }

        # Merge analytics, constant field overrides and meta fields into one dict
        logstash_message = {**record_fields, **self.constant_fields, **meta_fields}

        return self.serialize(logstash_message)


class AstrosatAppTCPLogstashLogHandler(TCPLogstashHandler):
    """
    Sends JSON log records to Logstash over TCP as line-seperated JSON documents
    compatible with the Logstash TCP input plugin.
    Adds extra metadata fields to each record about the app instance.
    """

    def __init__(self, host, port, app, instance, environment, stream="default"):
        super(TCPLogstashHandler, self).__init__(host, port)

        self.formatter = ElasticsearchDocumentLogFormatter(constant_fields={
            "app": app,
            "instance": instance,
            "environment": environment,
            "stream": stream,
        })
