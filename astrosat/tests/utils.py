import pytest
import factory
import io
import os
from collections import namedtuple
from itertools import combinations
from random import shuffle

from django.contrib.auth import get_user_model
from django.core.files.storage import get_storage_class
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from astrosat.utils import DataClient
from .factories import UserFactory

##############
# useful fns #
##############


def shuffle_string(string):
    """
    Mixes up a string.
    Useful for generating invalid ids, etc.
    """
    string_list = list(string)
    shuffle(string_list)
    return "".join(string_list)


#############
# factories #
#############


def optional_declaration(declaration, chance=50, default=None):
    """
    Used in DjangoModelFactories.  Only sets a field value to
    "declaration" some of the time, otherwise sets it to "default".
    Useful for optional fields.
    """

    return factory.Maybe(
        factory.Faker("boolean", chance_of_getting_true=chance),
        yes_declaration=declaration,
        no_declaration=default,
    )


###########
# markers #
###########


def get_list_combinations(lst):
    """
    Returns all possible list combination of lst.
    >> get_list_combinations(["a", "b", "c"])
    >> [[], ["a"], ["b"], ["c"], ["a", "b"], ["a", "c"], ["b", "c"], ["a", "b", "c"]]
    useful w/ `@pytest.mark.parametrize`
    """
    n_items = len(lst) + 1
    lists = []
    for i in range(0, n_items):
        temp = [list(c) for c in combinations(lst, i)]
        if len(temp):
            lists.extend(temp)
    return lists


#####################
# fixtures  & mocks #
#####################

MockDataClientPathInfo = namedtuple(
    # the mocker uses this structure to associate
    # the local path with the (pretend) remote key
    "MockDataClientPathInfo",
    ["path", "key"],
)


@pytest.fixture
def mock_data_client(monkeypatch):
    """
    Returns a DataClient which overrides the default behavior
    of its adapted AWS client so that it uses stubbed data
    (stored in local files), rather than trying to access a
    remote connection during testing.

    Takes a list of information about the local paths to use.
    """
    def _mock_data_client(data_paths):

        data_paths = [
            MockDataClientPathInfo(*data_path) for data_path in data_paths
        ]

        def list_objects_v2(*args, **kwargs):
            objs = [{"Key": data_path.key} for data_path in data_paths]
            return {"Contents": objs}

        def get_object(*args, **kwargs):
            key = kwargs.pop("Key")
            for data_path in data_paths:
                if data_path.key == key:
                    obj = open(data_path.path, "rb")
                    return {"Body": obj}
            return None

        data_client = DataClient()
        adapted_data_client_class = type(data_client.client)

        def init(self, *args, **kwargs):
            # make sure that data_client uses the patched adapted_data_client_class
            self.client = data_client.client

        monkeypatch.setattr(
            adapted_data_client_class, "list_objects_v2", list_objects_v2
        )
        monkeypatch.setattr(adapted_data_client_class, "get_object", get_object)
        monkeypatch.setattr(DataClient, "__init__", init)

        return data_client

    return _mock_data_client


@pytest.fixture
def mock_storage(monkeypatch):
    """
    Mocks the backend storage system by not actually accessing media
    """

    clean_name = lambda name: os.path.splitext(os.path.basename(name))[0]

    def _mock_open(instance, name, mode="rb"):
        return SimpleUploadedFile(name=name, content=b"mock")

    def _mock_save(instance, name, content):
        setattr(instance, f"mock_{clean_name(name)}_exists", True)
        return str(name).replace("\\", "/")

    def _mock_delete(instance, name):
        setattr(instance, f"mock_{clean_name(name)}_exists", False)
        pass

    def _mock_exists(instance, name):
        return getattr(instance, f"mock_{clean_name(name)}_exists", False)

    # TODO: APPLY MOCK TO DefaultStorage AS WELL
    storage_class = get_storage_class()

    monkeypatch.setattr(storage_class, "_open", _mock_open)
    monkeypatch.setattr(storage_class, "_save", _mock_save)
    monkeypatch.setattr(storage_class, "delete", _mock_delete)
    monkeypatch.setattr(storage_class, "exists", _mock_exists)
