import factory
from factory.faker import Faker as FactoryFaker  # note I use FactoryBoy's wrapper of Faker

from astrosat.tests.providers import GeometryProvider, ValidatedProvider
from astrosat.tests.utils import optional_declaration

from example.models import (
    ExampleBulkModel,
    ExampleEpochModel,
    ExampleHashableModel,
    ExampleSingletonModel,
)


FactoryFaker.add_provider(GeometryProvider)
FactoryFaker.add_provider(ValidatedProvider)


class ExampleHashableModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExampleHashableModel

    name = FactoryFaker("name")


class ExampleSingletonModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExampleSingletonModel

    name = FactoryFaker("name")


# class ExampleGeoModelFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = ExampleGeoModel

#     name = FactoryFaker("name")
#     geometry = FactoryFaker("point")


class ExampleBulkModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExampleBulkModel

    something_unique = FactoryFaker(
        "validated_word",
        validators=[lambda x: not ExampleBulkModel.objects.filter(something_unique=x).exists()] + ExampleBulkModel._meta.get_field("something_unique").validators
    )
    something_non_unique = FactoryFaker("word")


class ExampleEpochModelFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExampleEpochModel

    name = FactoryFaker("name")
    date = FactoryFaker("date")
    tz_aware_date = FactoryFaker("date_time")
