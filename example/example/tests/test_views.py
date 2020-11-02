import pytest
import io
import json
import os
import urllib

from django.urls import reverse
from rest_framework import status

from astrosat.tests.utils import mock_data_client

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEST_DATA_PATHS = [
    (os.path.join(TEST_DATA_DIR, file_name), file_name)  # path  # key
    for file_name in os.listdir(TEST_DATA_DIR)
]


@pytest.mark.django_db
def test_proxy_s3_view(api_client, mock_data_client):

    # note that the proxy view returns a StreamingHttpResponse
    # this explains why I have to convert its value to BytesIO below

    view_name = "proxy-s3"
    data_client = mock_data_client(TEST_DATA_PATHS)

    # test a valid key returns the expected resource...
    valid_url_params = urllib.parse.urlencode({"key": "one.json"})
    url = f"{reverse(view_name)}?{valid_url_params}"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    content = json.load(io.BytesIO(response.getvalue()))
    assert content["name"] == "one"
    assert content["value"] == 1

    # test an invalid key returns an error...
    invalid_url_params = urllib.parse.urlencode({"key": "invalid"})
    url = f"{reverse(view_name)}?{invalid_url_params}"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
