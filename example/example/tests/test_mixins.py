import pytest
from django.db import models
from example.models import ExampleSingletonModel
from . import factories


@pytest.mark.django_db
class TestHashable:
    def test_hash_created(self):

        test_model = factories.ExampleHashableModelFactory()
        test_model.refresh_from_db(
        )  # need to let the hash be converted back to a UUID

        assert test_model.hash is not None

    def test_hash_required(self, monkeypatch):

        with pytest.raises(NotImplementedError):
            monkeypatch.delattr(
                # remove the 'hash_source' property from ExampleHashableModel
                "example.models.ExampleHashableModel.hash_source"
            )
            test_model = factories.ExampleHashableModelFactory()

    def test_hash_changed(self):

        old_name = "old name"
        new_name = "new name"
        test_model = factories.ExampleHashableModelFactory(name=old_name)
        test_model.refresh_from_db(
        )  # need to let the hash be converted back to a UUID

        assert test_model.has_hash_source_changed(old_name.encode()) is False
        assert test_model.has_hash_source_changed(new_name.encode()) is True


@pytest.mark.django_db
class TestSingleton:
    def test_cannot_have_more_than_one_singleton(self):

        number_of_singletons = ExampleSingletonModel.objects.count()
        assert number_of_singletons == 0
        singleton = ExampleSingletonModel(name="valeria")
        singleton.save()
        singleton2 = ExampleSingletonModel(name="test2")
        singleton2.save()
        number_of_singletons = ExampleSingletonModel.objects.count()
        assert number_of_singletons == 1
        assert singleton2.id == None
        assert singleton.id != None
