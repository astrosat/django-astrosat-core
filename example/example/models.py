from functools import partial

from django.conf import settings
from django.db import models

# from django.contrib.gis.db import models as gis_models

from astrosat.fields import EpochField, LazyCharArrayField
from astrosat.mixins import HashableMixin, SingletonMixin
from astrosat.utils import CONDITIONAL_CASCADE
"""
A bunch of models that are just used for testing
"""


class ExampleHashableModel(HashableMixin, models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

    @property
    def hash_source(self):
        return self.name.encode()


class ExampleSingletonModel(SingletonMixin, models.Model):

    name = models.CharField(max_length=255)
    flag = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


# class ExampleGeoModel(gis_models.Model):

#     name = models.CharField(max_length=255)
#     geometry = gis_models.PointField()


class ExampleBulkModel(models.Model):

    something_unique = models.CharField(max_length=255, unique=True)
    something_non_unique = models.CharField(max_length=255)


class ExampleEpochModel(models.Model):

    name = models.CharField(max_length=255)
    date = EpochField(format="%Y-%m-%d", null=True, blank=True)
    tz_aware_date = EpochField(
        format="%Y-%m-%d %H:%M:%S", null=True, blank=True
    )


# class ExampleLazyCharArrayModel(models.Model):

#     name = models.CharField(max_length=255)
#     list_of_things = LazyCharArrayField(
#         models.CharField(max_length=255, blank=True, null=True),
#         null=True, blank=True,
#     )


class ExampleUnloadableModelManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ExampleUnloadableParentModel(models.Model):

    objects = ExampleUnloadableModelManager()

    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return f"{self.name}"

    def natural_key(self):
        return (self.name, )


class ExampleUnloadableChildModel(models.Model):

    objects = ExampleUnloadableModelManager()

    name = models.CharField(unique=True, max_length=255)
    parent = models.ForeignKey(
        ExampleUnloadableParentModel,
        on_delete=models.CASCADE,
        related_name="children"
    )

    def __str__(self):
        return f"{self.name}"

    def natural_key(self):
        return (self.name, )


class ExampleConditionallyDeletedThing(models.Model):

    name = models.CharField(unique=True, max_length=255)
    should_delete = models.BooleanField(default=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=partial(
            CONDITIONAL_CASCADE,
            condition={"should_delete": True},
            default_value=None
        ),
        related_name="things",
    )

    def __str__(self):
        return f"{self.name}"
