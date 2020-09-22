import factory
from factory.faker import (
    Faker as FactoryFaker,
)  # note I use FactoryBoy's wrapper of Faker

from astrosat.tests.providers import GeometryProvider, ValidatedProvider
from astrosat.tests.utils import optional_declaration

from example.models import (
    ExampleBulkModel,
    ExampleEpochModel,
    ExampleHashableModel,
    ExampleSingletonModel,
    ExampleUnloadableParentModel,
    ExampleUnloadableChildModel,
)


FactoryFaker.add_provider(GeometryProvider)
FactoryFaker.add_provider(ValidatedProvider)


class ExampleHashableModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleHashableModel

    name = FactoryFaker("name")


class ExampleSingletonModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleSingletonModel

    name = FactoryFaker("name")


# class ExampleGeoModelFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = ExampleGeoModel

#     name = FactoryFaker("name")
#     geometry = FactoryFaker("point")


class ExampleBulkModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleBulkModel

    something_unique = FactoryFaker(
        "validated_word",
        validators=[
            lambda x: not ExampleBulkModel.objects.filter(something_unique=x).exists()
        ]
        + ExampleBulkModel._meta.get_field("something_unique").validators,
    )
    something_non_unique = FactoryFaker("word")


class ExampleEpochModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleEpochModel

    name = FactoryFaker("name")
    date = FactoryFaker("date")
    tz_aware_date = FactoryFaker("date_time")


class ExampleUnloadableParentModel(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleUnloadableParentModel

    name = factory.LazyAttributeSequence(lambda o, n: f"parent-{n}")


class ExampleUnloadableChildModel(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleUnloadableChildModel

    name = factory.LazyAttributeSequence(lambda o, n: f"child-{n}")
    parent = factory.SubFactory(ExampleUnloadableParentModel)
