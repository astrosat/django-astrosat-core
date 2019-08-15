from django.db import models
# from django.contrib.gis.db import models as gis_models

from astrosat.fields import EpochField, LazyCharArrayField
from astrosat.mixins import HashableMixin, SingletonMixin


"""
A bunch of models that are just used for testing
"""


class ExampleHashableModel(HashableMixin, models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @property
    def hash_source(self):
        return self.name.encode()


class ExampleSingletonModel(SingletonMixin, models.Model):

    name = models.CharField(max_length=255)
    flag = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# class ExampleGeoModel(gis_models.Model):

#     name = models.CharField(max_length=255)
#     geometry = gis_models.PointField()


class ExampleBulkModel(models.Model):

    something_unique = models.CharField(max_length=255, unique=True)
    something_non_unique = models.CharField(max_length=255)


class ExampleEpochModel(models.Model):

    name = models.CharField(max_length=255)
    date = EpochField(format="%Y-%m-%d", null=True, blank=True)
    tz_aware_date = EpochField(format="%Y-%m-%d %H:%M:%S", null=True, blank=True)


# class ExampleLazyCharArrayModel(models.Model):

#     name = models.CharField(max_length=255)
#     list_of_things = LazyCharArrayField(
#         models.CharField(max_length=255, blank=True, null=True),
#         null=True, blank=True,
#     )
