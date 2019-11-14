import factory
import pytest
from time import time
from django.db import models

from astrosat.utils import bulk_update_or_create
from example.models import ExampleBulkModel

from . import factories


def old_update_or_create(model_data):
    """
    This fn is an example of the standard Django way of updating or creating a batch of items.
    Because this project often deals w/ huge datasets, I wrote the fn bulk_update_or_create.
    This achieves the same thing faster and w/ less db hits.

    The tests in this module just make sure that bulk_update_or_create remains more efficient.
    """

    created = []
    updated = []

    for data in model_data:
        obj, _created = ExampleBulkModel.objects.update_or_create(
            something_unique=data["something_unique"],
            defaults={"something_non_unique": data["something_non_unique"]},
        )
        if _created:
            created.append(obj)
        else:
            updated.append(obj)

    return (created, updated)


@pytest.fixture
def fake_bulk_model_data():
    """
    Generate a list of serialized ExampleBulkModels
    """

    def _fake_bulk_model_data(n_models):

        max_attempts = 1000
        attempt = 0

        data = []

        while len(data) < n_models:

            attempt += 1

            data_record = factory.build(
                dict, FACTORY_CLASS=factories.ExampleBulkModelFactory
            )
            if next(
                (
                    x
                    for x in data
                    if x["something_unique"] == data_record["something_unique"]
                ),
                None,
            ):
                continue

            data.append(data_record)

            if attempt >= max_attempts:
                msg = f"Exceeded {attempt} attempts to generate a unique FakeBulkModel"
                raise ValidationError(msg)

        return data

    return _fake_bulk_model_data


@pytest.mark.django_db
class TestBulkUpdateOrCreate:

    N_QUERIES = (
        3
    )  # should never do more than 3 queries: 1 to check exisiting objects, 1 to update, 1 to create

    def test_create_objects(self, fake_bulk_model_data, django_assert_max_num_queries):

        test_data = fake_bulk_model_data(10)

        assert ExampleBulkModel.objects.count() == 0

        with django_assert_max_num_queries(self.N_QUERIES):
            created, updated = bulk_update_or_create(ExampleBulkModel, test_data)
            assert len(created) == 10
            assert len(updated) == 0

        assert ExampleBulkModel.objects.count() == 10

    def test_update_objects(self, fake_bulk_model_data, django_assert_max_num_queries):

        test_data = fake_bulk_model_data(10)

        bulk_update_or_create(ExampleBulkModel, test_data)
        assert ExampleBulkModel.objects.count() == 10

        for data in test_data:
            data["something_non_unique"] = "updated"

        with django_assert_max_num_queries(self.N_QUERIES):
            created, updated = bulk_update_or_create(ExampleBulkModel, test_data)
            assert len(created) == 0
            assert len(updated) == 10

        assert ExampleBulkModel.objects.count() == 10
        assert (
            ExampleBulkModel.objects.filter(something_non_unique="updated").count()
            == 10
        )

    def test_update_and_create_objects(
        self, fake_bulk_model_data, django_assert_max_num_queries
    ):

        test_data = fake_bulk_model_data(10)

        bulk_update_or_create(ExampleBulkModel, test_data[:5])
        assert ExampleBulkModel.objects.count() == 5

        for data in test_data:
            data["something_non_unique"] = "updated"

        with django_assert_max_num_queries(self.N_QUERIES):
            created, updated = bulk_update_or_create(ExampleBulkModel, test_data)
            assert len(created) == 5
            assert len(updated) == 5

        assert ExampleBulkModel.objects.count() == 10
        assert (
            ExampleBulkModel.objects.filter(something_non_unique="updated").count()
            == 10
        )

    def test_comparator_fn(self, fake_bulk_model_data):

        test_data = fake_bulk_model_data(2)
        bulk_update_or_create(ExampleBulkModel, test_data)
        assert ExampleBulkModel.objects.count() == 2

        test_data[0]["something_non_unique"] = "passes"
        test_data[1]["something_non_unique"] = "fails"

        comparator_fn = (
            lambda matching_object, data_record: data_record["something_non_unique"]
            == "passes"
        )

        # should only update 1 instance b/c the comparator_fn will fail w/ test_data[1]
        created, updated = bulk_update_or_create(
            ExampleBulkModel, test_data, comparator_fn=comparator_fn
        )
        assert len(created) == 0
        assert len(updated) == 1

        assert (
            ExampleBulkModel.objects.get(
                something_unique=test_data[0]["something_unique"]
            ).something_non_unique
            != "passes"
        )

    def test_invalid_data(self):

        # this is invalid data b/c it is missing the unique fields
        test_data = [{"something_non_unique": "valid data"}]

        with pytest.raises(KeyError):
            bulk_update_or_create(ExampleBulkModel, test_data)

    def test_faster(self, fake_bulk_model_data):

        test_data = fake_bulk_model_data(100)

        # old method of creating
        t = time()
        old_create_created, old_create_updated = old_update_or_create(test_data)
        old_create_time = time() - t

        # old method of updating
        t = time()
        old_update_created, old_update_updated = old_update_or_create(test_data)
        old_update_time = time() - t

        ExampleBulkModel.objects.all().delete()

        # new method of creating
        t = time()
        bulk_create_created, bulk_create_updated = bulk_update_or_create(
            ExampleBulkModel, test_data
        )
        bulk_create_time = time() - t

        # new method of updating
        t = time()
        bulk_update_created, bulk_update_updated = bulk_update_or_create(
            ExampleBulkModel, test_data
        )
        bulk_update_time = time() - t

        assert len(old_create_created) == len(bulk_create_created)
        assert len(old_create_updated) == len(bulk_create_updated)
        assert len(old_update_created) == len(bulk_update_created)
        assert len(old_update_updated) == len(bulk_update_updated)

        assert old_create_time > bulk_create_time
        assert old_update_time > bulk_update_time
