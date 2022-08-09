import os
import zipfile

from django.apps import apps
from django.core.management.base import CommandError
from django.core.management.commands.loaddata import Command as DjangoLoadDataCommand
from django.db.models.fields.files import FileField, ImageField
from django.db.models.signals import pre_save

MEDIA_FIELDS = [FileField, ImageField]


def is_media_field(field):
    return any(isinstance(field, field_class) for field_class in MEDIA_FIELDS)


def get_models_with_media_fields():
    for ModelClass in apps.get_models(
        include_auto_created=True, include_swapped=True
    ):
        if any(is_media_field(field) for field in ModelClass._meta.fields):
            yield ModelClass


class Command(DjangoLoadDataCommand):
    """
    Just like the built-in loaddata command, except optionally uses the `pre_save` signal
    to move any media files to the appropriate media storage location.  Media files are either
    located in a local directory or zipfile (specified by --media-path) or else in "<app>/fixtures/media".
    """
    def load_media(self, sender, *args, **kwargs):

        instance = kwargs["instance"]

        # work out where fixture media files for this model ought to live...
        if not self.media_path:
            app_path = apps.get_app_config(sender._meta.app_label).path
            app_fixture_media_path = os.path.join(app_path, "fixtures/media")
        else:
            app_fixture_media_path = self.media_path

        for field in sender._meta.fields:

            if not is_media_field(field):
                continue

            media_file = getattr(instance, field.name)
            if media_file:
                # get the path for this fixture media file...
                media_file_full_name = media_file.name
                media_file_fixture_path = os.path.join(
                    app_fixture_media_path, media_file_full_name
                )
                try:
                    # try to read the file...
                    with open(media_file_fixture_path, "rb") as fp:
                        if field.storage.exists(media_file_full_name):
                            field.storage.delete(media_file_full_name)
                        # ...and write it to storage...
                        field.storage.save(media_file_full_name, fp)
                except Exception as e:
                    # if anything went wrong, print the error,
                    # but keep processing the fixture...
                    msg = f"Error storing '{instance}.{field.name}': {e}"
                    self.stderr.write(self.style.WARNING(msg))

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--media",
            dest="load_media",
            action="store_true",
            help="Include storing media when importing serialized data.",
        )

        parser.add_argument(
            "--media-path",
            dest="media_path",
            help="location of dir w/ media files",
        )

    def handle(self, *fixture_labels, **options):

        load_media = options["load_media"]
        media_path = options["media_path"]

        # figure out where media files are stored...
        if load_media:
            if media_path:
                media_abspath = os.path.abspath(media_path)
                media_dir, media_file = os.path.split(media_abspath)
                if zipfile.is_zipfile(media_abspath):
                    with zipfile.ZipFile(media_abspath, "r") as zip:
                        zip.extractall(media_dir)
                    self.media_path = os.path.join(
                        media_dir, os.path.splitext(media_file)[0]
                    )
                elif os.path.isdir(media_abspath):
                    self.media_path = media_abspath
                else:
                    raise CommandError(
                        f"{media_path} must either be a zipfile or a directory"
                    )

            else:
                self.media_path = None

        # intercept media fields...
        if load_media:
            for ModelClass in get_models_with_media_fields():
                pre_save.connect(self.load_media, sender=ModelClass)

        # load data...
        command_result = super().handle(*fixture_labels, **options)

        # stop intercepting media fields...
        if load_media:
            for ModelClass in get_models_with_media_fields():
                pre_save.disconnect(self.load_media, sender=ModelClass)

        return command_result
