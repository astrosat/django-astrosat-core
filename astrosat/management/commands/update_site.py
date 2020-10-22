import environ

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

env = environ.Env()

SITE_ENVIRONMENT_VARIABLE = "DJANGO_SITE_DOMAIN"


class Command(BaseCommand):
    """
    Updates the Sites table.
    """

    help = "Updates a Site object w/ a specific domain."

    def add_arguments(self, parser):

        parser.add_argument(
            "--id",
            dest="id",
            default=settings.SITE_ID,
            required=False,
            help=
            "id of Site to update (if unprovied will use the default SITE_ID specified in settings).",
        )

        parser.add_argument(
            "--domain",
            dest="domain",
            required=False,
            default=None,
            help=
            f"Domain to update the Site with (if unprovided will use the {SITE_ENVIRONMENT_VARIABLE} environment variable).",
        )

        parser.add_argument(
            "--name",
            dest="name",
            required=False,
            default=None,
            help=
            "Name to update the Site with (if unprovided will just use the domain).",
        )

    def handle(self, *args, **options):

        try:

            domain = (
                options["domain"] if options["domain"] is not None else
                env(SITE_ENVIRONMENT_VARIABLE)
            )
            name = options["name"] if options["name"] is not None else domain

            Site.objects.update_or_create(
                id=options["id"],
                defaults={
                    "domain": domain[:100],
                    "name": name[:50]
                }
            )

        except ImproperlyConfigured:
            raise CommandError(
                "You must either specify a domain on the command-line or set the DJANGO_SITE_DOMAIN environment variable."
            )

        except IntegrityError:
            raise CommandError(f"The domain '{domain}' is already in use.")

        except Exception as e:
            raise CommandError(str(e))
