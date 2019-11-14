import pytest
import io

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from astrosat.tests.factories import UserFactory


@pytest.fixture
def api_client():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def create_env_file():
    def _create_env_file(**kwargs):

        assert len(kwargs) >= 1

        env_file = io.StringIO()
        for key, value in kwargs.items():
            env_file.write(f"{key}={value}\n")
        env_file.seek(0)

        return env_file

    return _create_env_file
