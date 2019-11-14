import datetime
import pytest
import pytz

from django.core.exceptions import ValidationError

from example.models import ExampleEpochModel
from .factories import ExampleEpochModelFactory


@pytest.mark.django_db
class TestEpoch:
    def test_initialise(self):
        fake_str = "2000-01-01"
        fake_date = datetime.datetime.strptime(fake_str, "%Y-%m-%d")
        fake_epoch = 946684800

        epoch_model = ExampleEpochModelFactory(date=fake_str)
        epoch_model.refresh_from_db()
        assert epoch_model.date == fake_epoch

        epoch_model = ExampleEpochModelFactory(date=fake_date)
        epoch_model.refresh_from_db()
        assert epoch_model.date == fake_epoch

        epoch_model = ExampleEpochModelFactory(date=None)
        epoch_model.refresh_from_db()
        assert epoch_model.date is None

        epoch_model = ExampleEpochModelFactory(date="")
        epoch_model.refresh_from_db()
        assert epoch_model.date is None

    def test_invalid_format(self):
        with pytest.raises(ValidationError):
            fake_str = "i am not a date"
            epoch_model = ExampleEpochModelFactory(date=fake_str)
            epoch_model.refresh_from_db()

    def test_convert(self):
        fake_str = "2000-01-01"
        fake_date = datetime.datetime.strptime(fake_str, "%Y-%m-%d")

        epoch_model = ExampleEpochModelFactory(date=fake_str)
        epoch_model.refresh_from_db()
        assert epoch_model.date_as_datetime() == fake_date

    def test_timezones(self):
        pst_zone = pytz.timezone("America/Los_Angeles")
        est_zone = pytz.timezone("America/New_York")

        fake_date = datetime.datetime(2001, 1, 1, 1, 0, 0)  # add HH:MM:SS
        fake_pst_date = pst_zone.localize(fake_date)
        fake_est_date = est_zone.localize(fake_date)

        pst_epoch_model = ExampleEpochModelFactory(tz_aware_date=fake_pst_date)
        pst_epoch_model.refresh_from_db()
        est_epoch_model = ExampleEpochModelFactory(tz_aware_date=fake_est_date)
        est_epoch_model.refresh_from_db()

        pst_hour = pst_epoch_model.tz_aware_date_as_datetime().hour
        est_hour = est_epoch_model.tz_aware_date_as_datetime().hour

        assert pst_hour - est_hour == 3
