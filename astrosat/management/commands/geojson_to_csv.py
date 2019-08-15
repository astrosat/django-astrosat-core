import os

import pandas as pd
import geopandas as gpd

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Converts a GeoJSON file to a CSV file.
    """

    help = "Converts a GeoJSON file to a CSV file."

    def add_arguments(self, parser):

        parser.add_argument(
            "--input",
            dest="input_path",
            required=True,
            help="location of input GeoJSON file",
        )

        parser.add_argument(
            "--output",
            dest="output_path",
            required=True,
            help="location of output CSV file",
        )

        parser.add_argument(
            "--index",
            dest="index",
            action="store_true",
            help="whether or not to include the index in the output (default is False)."
        )
        self.parser = parser  # save the parser to use w/ error messages below

    def handle(self, *args, **options):

        input_path = os.path.abspath(options["input_path"])
        output_path = os.path.abspath(options["output_path"])
        include_index = options["index"]

        try:
            geo_data_frame = gpd.read_file(input_path)
            data_frame = pd.DataFrame(
                geo_data_frame.drop(columns="geometry")
            )
            data_frame.to_csv(output_path, index=include_index)
        except Exception as e:
            raise CommandError(str(e) + "\n\n" + self.parser.format_help())
