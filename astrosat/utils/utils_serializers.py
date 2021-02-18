from collections import defaultdict

from django.core.serializers.json import Serializer as JSONSerializer

# Note that this is a Django Serializer, not a Django-Rest-Framework Serializer


class ExcludableJSONSerializer(JSONSerializer):
    """
    A custom (JSON) Serializer that allows me to exclude specific fields.  Takes a new kwarg "excludes"
    whose format is ["model.field", "field"] where "model.field" means exclude the field "field" from the
    model "model" and just "field" means exclude the field "field" from any model.

    To use, update settings.py as per https://docs.djangoproject.com/en/3.0/ref/settings/#serialization-modules
    """

    def serialize(self, queryset, *args, **kwargs):
        self.excluded_fields = defaultdict(list)
        for field in kwargs.pop("excludes", []):
            try:
                model_name, field_name = field.split(".")
                self.excluded_fields[model_name].append(field_name)
            except ValueError:
                self.excluded_fields[None].append(field)

        return super().serialize(queryset, *args, **kwargs)

    def is_field_excluded(self, obj, field):
        model_name = obj._meta.model_name
        field_name = field.attname
        if (model_name in self.excluded_fields and
                field_name in self.excluded_fields[model_name]):
            return True
        elif (None in self.excluded_fields and
              field_name in self.excluded_fields[None]):
            return True
        return False

    def handle_field(self, obj, field):
        if not self.is_field_excluded(obj, field):
            super().handle_field(obj, field)

    def handle_fk_field(self, obj, field):
        if not self.is_field_excluded(obj, field):
            super().handle_fk_field(obj, field)

    def handle_m2m_field(self, obj, field):
        if not self.is_field_excluded(obj, field):
            super().handle_m2m_field(obj, field)


Serializer = ExcludableJSONSerializer
