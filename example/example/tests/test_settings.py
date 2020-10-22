import pytest
import environ
import os

from astrosat.utils import DynamicSetting
from example.models import ExampleSingletonModel


class TestSettings:
    """
    Includes some tests to confirm that environ.Env can read
    both from the OS Environment and an environment file.
    """

    env = environ.Env()

    def test_env_missing(self):

        env_key = "MISSING"
        env_value = "true"

        assert env_key not in os.environ
        assert self.env(env_key, default=env_value) == env_value

    def test_env_read_from_environment(self):

        env_key = "READ_FROM_ENVIRONMENT"
        env_value = "true"

        os.environ[env_key] = env_value

        assert self.env(env_key) == env_value

    def test_env_read_from_file(self, create_env_file):

        env_key = "READ_FROM_FILE"
        env_value = "true"

        env_file = create_env_file(**{env_key: env_value})
        self.env.read_env(env_file)

        assert self.env(env_key) == env_value

    def test_env_read_from_multiple_files(self, create_env_file):

        env_key_1 = "KEY1"
        env_key_2 = "KEY2"
        env_key_3 = "KEY3"

        env_files = [
            create_env_file(**{
                env_key_1: "one",
                env_key_2: "one"
            }),
            create_env_file(**{
                env_key_2: "two",
                env_key_3: "two"
            }),
        ]

        for env_file in reversed(env_files):
            # TODO: django-environ does not overwrite existing environment variables
            # TODO: hence the call to `reversed` above
            # TODO: but there is a PR to do this: https://github.com/joke2k/django-environ/pull/191
            self.env.read_env(env_file)

        assert self.env(env_key_1) == "one"
        assert self.env(env_key_2) == "two"
        assert self.env(env_key_3) == "two"

    def test_env_read_from_both(self, create_env_file):

        environment_env_key = "READ_FROM_ENVIRONMENT"
        environment_env_value = "true"

        file_env_key = "READ_FROM_FILE"
        file_env_value = "true"

        os.environ[environment_env_key] = environment_env_value
        env_file = create_env_file(**{file_env_key: file_env_value})
        self.env.read_env(env_file)

        assert self.env(environment_env_key) == environment_env_value
        assert self.env(file_env_key) == file_env_value


class TestDynamicSettings:
    @pytest.mark.django_db
    def test_dynamic_settings(self, settings):

        settings.TEST_FLAG = DynamicSetting(
            "example.ExampleSingletonModel.flag", False
        )

        assert ExampleSingletonModel.objects.count() == 0

        # test that accessing the setting created the source w/ the default_value...
        assert settings.TEST_FLAG == False
        assert ExampleSingletonModel.objects.count() == 1

        # change the source's value...
        test_singleton = ExampleSingletonModel.load()
        test_singleton.flag = True
        test_singleton.save()

        # test that accessing the setting again returns the newly-changed value...
        assert settings.TEST_FLAG == True
        assert ExampleSingletonModel.objects.count() == 1
