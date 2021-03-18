import json
from datetime import datetime
from logstash.handler_tcp import TCPLogstashHandler
from logstash.formatter import LogstashFormatterBase

def format_elasticsearch_timestamp(time):
    "Renders a timestamp in the format expected by elasticsearch"
    return LogstashFormatterBase.format_timestamp(time)


class AstrosatAnalyticsLogstashFormatter(LogstashFormatterBase):
    # Based on LogstashFormatterBase/Version1
    # from python-logstash
    # https://github.com/vklochan/python-logstash/blob/master/logstash/formatter.py
    def __init__(self, overrides=dict()):
        self.overrides = overrides

    def format(self, record):

        analytics_fields = json.loads(record.getMessage())

        meta_fields = {
            "@timestamp": format_elasticsearch_timestamp(record.created),
            "@version": 1,
        }

        # Merge analytics, overrides and meta fields into one dict
        logstash_message = {**analytics_fields, **self.overrides, **meta_fields}

        return self.serialize(logstash_message)

class AstrosatAnalyticsTCPLogstashHandler(TCPLogstashHandler):

    def __init__(self, host, port, app, instance, environment, stream="default"):
        super(TCPLogstashHandler, self).__init__(host, port)

        self.formatter = AstrosatAnalyticsLogstashFormatter(overrides={
            "app": app,
            "instance": instance,
            "environment": environment,
            "stream": stream,
        })
