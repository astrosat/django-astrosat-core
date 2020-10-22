import json

from django.contrib.gis.geos import GEOSGeometry


def adapt_geojson_to_django(geojson, geometry_field_name="geometry"):
    """
    You cannot deserialize raw GeoJSON to GeoDjango.
    So this fn takes raw GeoJSON and turns it into something that _can_ be serialized.
    """
    for feature in geojson["features"]:
        fields = feature["properties"]
        fields.update(
            {
                geometry_field_name:
                    GEOSGeometry(json.dumps(feature["geometry"]))
            }
        )
        yield fields
