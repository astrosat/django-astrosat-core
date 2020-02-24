from jsonschema import validate

from django.core.exceptions import ValidationError
from django.utils.html import strip_tags


def validate_no_spaces(value):

    if " " in value:
        msg = f"Value must not contain spaces."
        raise ValidationError(msg)


def validate_no_tags(value):

    if value != strip_tags(value):
        msg = f"Value may not contain tags."
        raise ValidationError(msg)


def validate_reserved_words(value, reserved_words, case_insensitive=False):
    if (case_insensitive and value.lower() in map(str.lower, reserved_words)) or (
        value in reserved_words
    ):
        msg = f"{value} is a reserved word."
        raise ValidationError(msg)


def validate_schema(value, schema):
    try:
        validate(instance=value, schema=schema)
    except Exception as e:
        msg = str(e)
        raise ValidationError(msg)
