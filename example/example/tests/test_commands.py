import pytest
import environ

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management import CommandError, call_command

from astrosat.management.commands.update_site import SITE_ENVIRONMENT_VARIABLE


@pytest.mark.django_db
class TestUpdateSite():

    command_name = "update_site"

    def test_update_site(self):

        test_domain = "test_domain"
        test_name = "test_name"

        site = Site.objects.get(id=settings.SITE_ID)
        assert site.domain != test_domain
        assert site.name != test_name

        call_command(self.command_name, domain=test_domain)
        site.refresh_from_db()
        assert Site.objects.count() == 1

        # make sure we changed the domain and set the name to the domain
        assert site.domain == test_domain
        assert site.name == test_domain

        call_command(self.command_name, domain=test_domain, name=test_name)
        site.refresh_from_db()
        assert Site.objects.count() == 1

        # make sure we changed the domain and name
        assert site.domain == test_domain
        assert site.name == test_name

    def test_update_site_additional_site(self):

        test_domain = "test_domain"
        test_name = "test_name"
        test_id = settings.SITE_ID + 1

        call_command(self.command_name, domain=test_domain, name=test_name, id=test_id)
        assert Site.objects.count() == 2

        # make sure the new site has the correct values
        site = Site.objects.get(id=test_id)
        assert site.domain == test_domain
        assert site.name == test_name

        # make sure we can't specify a duplicate domain
        with pytest.raises(CommandError):
            another_test_id = test_id + 1
            call_command(self.command_name, domain=test_domain, name=test_name, id=another_test_id)
        assert Site.objects.count() == 2

    def test_update_site_from_env(self, create_env_file):

        # make sure we can't update a site w/out a domain
        with pytest.raises(CommandError):
            call_command(self.command_name)

        # make sure we can update a site using the environment
        test_domain = "environment_domain"
        env = environ.Env()
        env_file = create_env_file(**{SITE_ENVIRONMENT_VARIABLE: test_domain})
        env.read_env(env_file)
        call_command(self.command_name)
        site = Site.objects.get(id=settings.SITE_ID)
        assert site.domain == test_domain
        assert site.name == test_domain
