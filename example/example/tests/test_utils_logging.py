import datetime
import logging
import pytest

from django.urls import resolve, reverse

from rest_framework import status

from astrosat.models import DatabaseLogRecord, DatabaseLogTag
from .factories import *


@pytest.mark.django_db
def test_logging():

    logger = logging.getLogger("db")

    assert DatabaseLogRecord.objects.count() == 0
    assert DatabaseLogTag.objects.count() == 0

    # create a DatabaseLogRecord w/ no tags...
    logger.debug("test1")
    assert DatabaseLogRecord.objects.count() == 1
    assert DatabaseLogTag.objects.count() == 0
    log_record = DatabaseLogRecord.objects.get(message="test1")
    tags = log_record.tags.all()
    assert log_record.level == logging.DEBUG
    assert log_record.message == "test1"
    assert len(tags) == 0


    # create a DatabaseLogRecord w/ 1 tag...
    logger.debug("test2", extra={"tags": ["tag1"]})
    assert DatabaseLogRecord.objects.count() == 2
    assert DatabaseLogTag.objects.count() == 1
    log_record = DatabaseLogRecord.objects.get(message="test2")
    tags = log_record.tags.all()
    assert log_record.level == logging.DEBUG
    assert log_record.message == "test2"
    assert len(tags) == 1

    # create a DatabaseLogRecord w/ 2 tags (1 new, 1 existing)...
    logger.debug("test3", extra={"tags": ["tag1", "tag2"]})
    assert DatabaseLogRecord.objects.count() == 3
    assert DatabaseLogTag.objects.count() == 2
    log_record = DatabaseLogRecord.objects.get(message="test3")
    tags = log_record.tags.all()
    assert log_record.level == logging.DEBUG
    assert log_record.message == "test3"
    assert len(tags) == 2
