import pytest
import io
import json
import os
import urllib

from django.urls import reverse
from rest_framework import status

from astrosat.tests.utils import mock_data_client

from astrosat.models import DatabaseLogRecord, DatabaseLogTag

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


@pytest.mark.django_db
class TestUserTracking:
    def test_submitting_invalid_json(self, api_client):
        """
        Ensure data posted to view is an array/list.
        """
        log_data = "content"

        url = reverse("log-tracking")

        response = api_client.post(url, log_data, format="json")

        assert not status.is_success(response.status_code)
        assert response.data == {
            "error": "Must supply an array of JSON objects in request"
        }

    def test_submitting_non_list(self, api_client):
        """
        Ensure data posted to view is an array/list.
        """
        log_data = {"content": {"key": "Value 1", }, "tags": ["dataset"]}

        url = reverse("log-tracking")

        response = api_client.post(url, log_data, format="json")

        assert not status.is_success(response.status_code)
        assert response.data == {
            "error": "Must supply an array of JSON objects in request"
        }

    def test_tracking_missing_content(self, api_client):
        """
        Ensure data posted to view has object called 'content'.
        """
        log_data = [{"key": "Value 1"}]

        url = reverse("log-tracking")

        response = api_client.post(url, log_data, format="json")

        assert not status.is_success(response.status_code)
        assert response.data == {
            "error":
                "Log Record must contain key 'content' of JSON to be logged"
        }

    def test_tracking_features(self, api_client, astrosat_settings):
        """
        Ensure correct data posted is handled.
        """
        # make sure logging is enabled...
        astrosat_settings.enable_db_logging = True
        astrosat_settings.save()
        log_data = [
            {
                "content": {
                    "key": "Value 1",
                },
                "tags": ["dataset"]
            }, {
                "content": {
                    "key": "Value 2",
                },
                "tags": ["dataset"]
            }
        ]

        url = reverse("log-tracking")

        assert DatabaseLogRecord.objects.count() == 0
        assert DatabaseLogTag.objects.count() == 0

        response = api_client.post(url, log_data, format="json")
        content = response.json()

        assert status.is_success(response.status_code)
        assert DatabaseLogRecord.objects.count() == 2
        assert DatabaseLogTag.objects.count() == 1

        for input_data, output_data in zip(log_data, content):
            assert json.dumps(input_data['content']) == output_data['message']
