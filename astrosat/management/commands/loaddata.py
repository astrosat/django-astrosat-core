import os

from django.apps import apps
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
    to move any media files from "app/fixures/media/<upload_to path>"
    to the appropriate media storage location.
    """
    def load_media(self, sender, *args, **kwargs):

        instance = kwargs["instance"]

        # work out where fixture media files for this model ought to live...
        app_path = apps.get_app_config(sender._meta.app_label).path
        app_fixture_media_path = os.path.join(app_path, "fixtures/media")

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
        parser.add_argument(
            "--media",
            action="store_true",
            help="Include storing media when importing serialized data.",
        )
        super().add_arguments(parser)

    def handle(self, *fixture_labels, **options):

        if options["media"]:
            for ModelClass in get_models_with_media_fields():
                pre_save.connect(self.load_media, sender=ModelClass)

        command_result = super().handle(*fixture_labels, **options)

        if options["media"]:
            for ModelClass in get_models_with_media_fields():
                pre_save.disconnect(self.load_media, sender=ModelClass)

        return command_result
