import datetime

from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import BigIntegerField
from django.core import exceptions


class EpochField(BigIntegerField):
    """
    Stores a date as an integer representing the epoch time.
    The corresponding date object can be retrieved using the `.<field_name>_as_datetime()` fn
    """

    def __init__(self, format="%Y-%m-%d", *args, **kwargs):
        self.format = format
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.format != "%Y-%m-%d":
            kwargs["format"] = self.format
        return name, path, args, kwargs

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Converts value in code (possibly a string or datetime object) to db format (integer)
        """
        if isinstance(value, str):
            # if it's a string, convert it to a date based on the current format
            try:
                value = datetime.datetime.strptime(value, self.format)
            except ValueError as e:
                if value == "" and self.blank:
                    value = None
                else:
                    raise exceptions.ValidationError(str(e))
        if isinstance(value, (datetime.datetime, datetime.date)):
            # if it's a date, convert it to an int
            return int(value.timestamp())
        return value  # otherwise, it's already been converted (or it's None)

    # no need to overwrite `to_python` b/c I want the serializer to use ints
    # def to_python(self, value):
    #     return super().to_python(value)

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Adds a `<field_name>_as_datetime()` fn to convert epoch to date
        """
        super().contribute_to_class(cls, name, **kwargs)

        def _epoch_to_date(instance, field_name=name):
            epoch = getattr(instance, field_name)
            return datetime.datetime.fromtimestamp(epoch)

        setattr(cls, f"{name}_as_datetime", _epoch_to_date)


class LazyCharArrayField(ArrayField):
    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Converts value in code (which may not be a list) to db format (list of base types)
        """

        if value is not None and not isinstance(value, list):
            return value.split(",")
        return value
