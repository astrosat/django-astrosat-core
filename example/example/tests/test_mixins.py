import pytest
from django.db import models

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
