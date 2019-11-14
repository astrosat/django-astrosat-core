import json
import os
import pytest

from urllib.parse import urlparse, parse_qs

from astrosat.tests.utils import mock_data_client


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEST_DATA_PATHS = [
    (os.path.join(TEST_DATA_DIR, file_name), file_name)  # path  # key
    for file_name in os.listdir(TEST_DATA_DIR)
]


def test_data_client(mock_data_client):
    """
    tests that the data_client's functions work
    (w/out actually making a remote AWS call)
    """

    data_client = mock_data_client(TEST_DATA_PATHS)

    # test get_all_matching_objects...
    matching_objects = data_client.get_all_matching_objects(".*")
    assert sum(1 for _ in matching_objects) == len(TEST_DATA_PATHS)
    matching_objects = data_client.get_all_matching_objects("^one.json$")
    assert sum(1 for _ in matching_objects) == 1
    matching_objects = data_client.get_all_matching_objects("^invalid$")
    assert sum(1 for _ in matching_objects) == 0

    # test get_first_matching_object...
    matching_object = data_client.get_first_matching_object("^invalid$")
    assert matching_object is None
    matching_object = data_client.get_first_matching_object("^two.json$")
    matching_object_content = json.load(matching_object.stream)
    assert matching_object_content["name"] == "two"
    assert matching_object_content["value"] == 2

    # test get_object...
    obj = data_client.get_object("one.json")
    obj_content = json.load(obj)
    assert obj_content["name"] == "one"
    assert obj_content["value"] == 1
    obj = data_client.get_object("invalid")
    assert obj is None

    # test get_data...
    data = data_client.get_data("^invalid$")
    assert data is None
    data = data_client.get_data("^one.json$")
    data_content = json.load(data)
    assert data_content["name"] == "one"
    assert data_content["value"] == 1

    # test get metadata only...
    matching_metadata_objects = data_client.get_all_matching_objects(
        ".*", metadata_only=True
    )
    for i, obj in enumerate(matching_metadata_objects, start=1):
        assert obj.stream is None
        assert obj.metadata is not None
    assert i == len(TEST_DATA_PATHS)

    # test get url...
    url = data_client.get_object_url("^one.json$")
    parsed_url = urlparse(url)
    assert parsed_url.path == "/one.json"
    # note that the next assertion will fail in CI where AWS Access Keys are not setup
    # checking the path above is enough to convince me the fn works, though
    # parsed_query_params = parse_qs(parsed_url.query)
    # assert set(parsed_query_params.keys()) == set(["AWSAccessKeyId", "Signature", "Expires"])
