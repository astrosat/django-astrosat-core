import collections
import gzip
import itertools
import os

from django.core import serializers
from django.core.management.base import CommandError
from django.core.management.commands.loaddata import (
    Command as DjangoLoadDataCommand,
    SingleZipReader,
)
from django.core.management.utils import parse_apps_and_model_labels
from django.db import connections, transaction


try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False

try:
    import lzma
    has_lzma = True
except ImportError:
    has_lzma = False


class Command(DjangoLoadDataCommand):
    """
    Unloads objects defined in a fixture file.  This is based off of the
    built-in loaddata management command b/c that already includes all of
    the logic for including/exluding specific apps, dealing w/ different
    compression formats, and - crucially - deserializing using natural_keys
    """

    help = "Deletes instances defined in the named fixture(s) from the database."

    def handle(self, *fixture_labels, **options):
        self.ignore = options["ignore"]
        self.using = options["database"]
        self.app_label = options["app_label"]
        self.verbosity = options["verbosity"]
        self.excluded_models, self.excluded_apps = parse_apps_and_model_labels(options["exclude"])
        self.format = options["format"]

        with transaction.atomic(using=self.using):
            # here is the different bit...
            self.unloaddata(fixture_labels)

        if transaction.get_autocommit(self.using):
            connections[self.using].close()

    def unloaddata(self, fixture_labels):
        connection = connections[self.using]

        self.fixture_count = 0
        self.unloaded_object_count = 0
        self.fixture_object_count = 0

        self.serialization_formats = serializers.get_public_serializer_formats()
        self.compression_formats = {
            None: (open, "rb"),
            "gz": (gzip.GzipFile, "rb"),
            "zip": (SingleZipReader, "r"),
            "stdin": (lambda *args: sys.stdin, None),
        }
        if has_bz2:
            self.compression_formats["bz2"] = (bz2.BZ2File, "r")
        if has_lzma:
            self.compression_formats["lzma"] = (lzma.LZMAFile, "r")
            self.compression_formats["xz"] = (lzma.LZMAFile, "r")

        for fixture_label in fixture_labels:
            if self.find_fixtures(fixture_label):
                break
        else:
            return

        # here is the different bit...
        # just execute the single unload_label fn, instead of all the
        # trial-and-error that happens when actually loading a fixture
        self.class_deletion_record = collections.defaultdict(int)
        for fixture_label in fixture_labels:
            self.unload_label(fixture_label)

        if self.verbosity >= 1:
            if self.fixture_object_count == self.unloaded_object_count:
                self.stdout.write(
                    "Unloaded %d object(s) from %d fixture(s)"
                    % (self.unloaded_object_count, self.fixture_count)
                )
            else:
                self.stdout.write(
                    "Unloaded %d object(s) (of %d) from %d fixture(s)"
                    % (
                        self.unloaded_object_count,
                        self.fixture_object_count,
                        self.fixture_count,
                    )
                )

    def unload_label(self, fixture_label):

        show_progress = self.verbosity >= 3
        for fixture_file, fixture_dir, fixture_name in self.find_fixtures(fixture_label):
            _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
            open_method, mode = self.compression_formats[cmp_fmt]
            fixture = open_method(fixture_file, mode)
            try:
                self.fixture_count += 1
                objects_in_fixture = 0
                unloaded_objects_in_fixture = 0
                if self.verbosity >= 2:
                    self.stdout.write(
                        "Installing %s fixture '%s' from %s."
                        % (ser_fmt, fixture_name, humanize(fixture_dir))
                    )

                objects = serializers.deserialize(
                    ser_fmt,
                    fixture,
                    using=self.using,
                    ignorenonexistent=self.ignore,
                    handle_forward_references=True,
                )

                for obj in objects:
                    objects_in_fixture += 1
                    if (
                        obj.object._meta.app_config in self.excluded_apps
                        or type(obj.object) in self.excluded_models
                    ):
                        continue

                    # here is the different bit...
                    obj_class_label = obj.object._meta.label
                    try:
                        n_deleted, deleted_classes = obj.object.delete(using=self.using)
                        unloaded_objects_in_fixture += n_deleted
                        for key, val in deleted_classes.items():
                            if key == obj_class_label:
                                self.class_deletion_record[key] += (val - 1)
                            else:
                                self.class_deletion_record[key] += val
                    except Exception as e:
                        # various exceptions might ocurr; if it is b/c the object has already been deleted
                        # then that's okay, just make a note of it and move on
                        if obj.object.pk is None:
                            if obj_class_label in self.class_deletion_record and self.class_deletion_record[obj_class_label] > 0:
                                self.class_deletion_record[obj_class_label] -= 1
                            pass
                        else:
                            raise

                    if show_progress:
                        self.stdout.write(
                            "\rProcessed %i object(s)." % unloaded_objects_in_fixture,
                            ending="",
                        )

                if objects and show_progress:
                    self.stdout.write()  # Add a newline after progress indicator.

                self.unloaded_object_count += unloaded_objects_in_fixture
                self.fixture_object_count += objects_in_fixture

            except Exception as e:
                if not isinstance(e, CommandError):
                    e.args = ("Problem unloading fixture '%s': %s" % (fixture_file, e),)
                raise
            finally:
                fixture.close()

            if objects_in_fixture == 0:
                warnings.warn(
                    "No fixture data found for '%s'. (File format may be "
                    "invalid.)" % fixture_name,
                    RuntimeWarning,
                )
