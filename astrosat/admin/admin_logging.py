import csv
import json

from django.contrib import admin
from django.http import HttpResponse

from astrosat.models import DatabaseLogTag, DatabaseLogRecord
from astrosat.serializers import DatabaseLogRecordSerializer

from .admin_base import DeleteOnlyModelAdminBase
from .admin_utils import IncludeExcludeListFilter, get_clickable_m2m_list_display


class TagListFilter(IncludeExcludeListFilter):

    include_empty_choice = True
    parameter_name = "tags"
    title = "tags"

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        return (
            (tag.pk, tag.name)
            for tag in DatabaseLogTag.objects.filter(pk__in=queryset.values("tags__pk"))
        )



@admin.register(DatabaseLogTag)
class DatabaseLogTagAdmin(admin.ModelAdmin):
    pass


@admin.register(DatabaseLogRecord)
class DatabaseLogRecordAdmin(DeleteOnlyModelAdminBase, admin.ModelAdmin):
    actions = ["export_as_csv"]
    date_hierarchy = "created"
    list_display = ("created", "level", "message", "get_tags_for_list_display")
    # TODO: ADD A DateRange FILTER (can use an actual form in the template)
    list_filter = ("level", TagListFilter)

    def get_queryset(self, request):
        # pre-fetching m2m fields that are used in list_displays
        # to avoid the "n+1" problem
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")

    def get_tags_for_list_display(self, obj):
        return get_clickable_m2m_list_display(DatabaseLogTag, obj.tags.all())

    get_tags_for_list_display.short_description = "tags"

    def export_as_csv(self, request, queryset):

        fields_to_export = ["id", "level", "created", "tags", "message"]
        headers = [f"record.{field}" for field in fields_to_export]
        extra_headers = set()
        data = []

        for record in DatabaseLogRecordSerializer(queryset, many=True).data:
            for header, field in zip(headers, fields_to_export):
                record[header] = record.pop(field)
            try:
                json_message = json.loads(record["record.message"])
                extra_headers.update(json_message.keys())
                record.update(json_message)
            except json.JSONDecodeError:
                pass
            data.append(record)

        headers = headers + sorted(extra_headers)

        csv_response = HttpResponse(content_type="text/csv")
        csv_response["Content-Disposition"] = f"attachment; filename=log_records.csv"
        writer = csv.writer(csv_response)
        writer.writerow(headers)
        writer.writerows(
            # add the row to the CSV; if a column doesn't exist just add None
            map(lambda row: [row.get(column, None) for column in headers], data)
        )

        return csv_response

    export_as_csv.short_description = "Export selected Log Records as CSV"
