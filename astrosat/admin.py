import csv
import json

from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.utils import flatten_fieldsets
from django.forms import widgets
from django.http import HttpResponse
from django.urls import resolve, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import AstrosatSettings, DatabaseLogTag, DatabaseLogRecord
from .serializers import DatabaseLogRecordSerializer


###########
# helpers #
###########


def get_clickable_m2m_list_display(model_class, queryset):
    """
    Prints a pretty (clickable) representation of a m2m field for an Admin's `list_display`.
    Note that when using this it is recommended to call `prefetch_related` in the Admin's
    `get_queryset` fn in order to avoid the "n+1" problem.
    """
    admin_change_url_name = f"admin:{model_class._meta.db_table}_change"
    list_display = [
        f"<a href='{reverse(admin_change_url_name, args=[obj.id])}'>{str(obj)}</a>"
        for obj in queryset
    ]
    return format_html(", ".join(list_display))


def get_clickable_fk_list_display(obj):
    """
    Prints a pretty (clickable) representation of a fk field for an Admin's `list_display`.
    """
    model_class = type(obj)
    admin_change_url_name = f"admin:{model_class._meta.db_table}_change"
    list_display = f"<a href='{reverse(admin_change_url_name, args=[obj.pk])}'>{str(obj)}</a>"
    return format_html(list_display)


class JSONAdminWidget(widgets.Textarea):

    def __init__(self, attrs=None):
        default_attrs = {
            # make things a bit bigger
            "cols": "80",
            "rows": "20",
            "class": "vLargeTextField",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2)
        except Exception:
            pass
        return value


class IncludeExcludeListFilter(admin.SimpleListFilter):
    """
    Lets me filter the listview on multiple values at once
    """

    # basic idea came from: https://github.com/ctxis/django-admin-multiple-choice-list-filter

    include_empty_choice = True
    parameter_name = None
    template = 'astrosat/admin/include_exclude_filter.html'
    title = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.lookup_kwarg = f"{self.parameter_name}__in"
        self.lookup_kwarg_isnull = f"{self.parameter_name}__isnull"
        _lookup_val = params.get(self.lookup_kwarg) or []
        _lookup_val_isnull = params.get(self.lookup_kwarg_isnull)
        self.lookup_val = _lookup_val.split(",") if _lookup_val else []
        self.lookup_val_isnull = _lookup_val_isnull == str(True)
        self._model_admin = model_admin

    def lookups(self, request, model_admin):
        raise NotImplementedError()

    def queryset(self, request, queryset):
        if self.lookup_val:
            queryset = queryset.filter(**{self.lookup_kwarg: self.lookup_val})
        if self.lookup_val_isnull:
            queryset = queryset.filter(**{self.lookup_kwarg_isnull: self.lookup_val_isnull})
        return queryset

    def choices(self, changelist):

        def _get_query_string(include=None, exclude=None):
            selections = self.lookup_val
            if include and include not in selections:
                selections.append(include)
            if exclude and exclude in selections:
                selections.remove(exclude)
            if selections:
                return changelist.get_query_string({self.lookup_kwarg: ",".join(selections)})
            else:
                return changelist.get_query_string(remove=[self.lookup_kwarg])

        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('Any'),
        }
        for lookup, val in self.lookup_choices:
            yield {
                'selected': str(lookup) in self.lookup_val,
                'query_string': changelist.get_query_string({self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]),
                'include_query_string': _get_query_string(include=str(lookup)),
                'exclude_query_string': _get_query_string(exclude=str(lookup)),
                'display': val,
            }
        if self.include_empty_choice:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string({self.lookup_kwarg_isnull: True}, [self.lookup_kwarg]),
                'display': self._model_admin.get_empty_value_display(),
            }


###############
# base admins #
###############


class CannotAddModelAdminBase(BaseModelAdmin):
    """
    Prevents adding new models via the admin
    """
    def has_add_permission(self, request, obj=None):
        return False


class CannotDeleteModelAdminBase(BaseModelAdmin):
    """
    Prevents deleting models via the admin
    """

    invalid_actions = ["delete_selected"]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):

        actions = super().get_actions(request)
        return {
            action_name: action_function
            for action_name, action_function in actions.items()
            if action_name not in self.invalid_actions
        }


class CannotUpdateModelAdminBase(BaseModelAdmin):
    """
    Prevents updating existing models via the admin
    """
    def changeform_view(
        self, request, object_id=None, form_url="", extra_context=None
    ):

        extra_context = extra_context or {}
        extra_context["show_save"] = False
        extra_context["show_save_and_continue"] = False
        # unfortunately, "show_save_and_add_another" is set dynamically by a template filter
        # which inexplicably completely ignores this context variable - bad bad django!
        # [https://github.com/django/django/blob/2.0.3/django/contrib/admin/templatetags/admin_modify.py#L59-L62]
        # hence, the ugly overloaded "has_add_permission" function below...
        extra_context["show_save_and_add_another"] = False
        return super().changeform_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def has_add_permission(self, request, obj=None):
        current_url = resolve(request.path_info).url_name
        if current_url.endswith("_change"):
            return False
        return True


class CannotEditModelAdminBase(BaseModelAdmin):
    """
    Prevents editing existing model fields via the admin
    """
    def get_readonly_fields(self, request, obj=None):

        # TODO: DOES THIS WORK FOR FIELDSETS?
        # fieldsets = self.get_fieldsets(request)
        # if fieldsets:
        #     return flatten_fieldsets(fieldsets)

        local_fields = list(
            set(
                # using 'local_fields' to exclude reverse relationships
                [f.name for f in self.opts.local_fields] +
                [f.name for f in self.opts.local_many_to_many]
            )
        )
        return local_fields


class ReadOnlyModelAdminBase(
    CannotAddModelAdminBase,
    CannotDeleteModelAdminBase,
    CannotUpdateModelAdminBase,
    CannotEditModelAdminBase,
):
    """"
    Prevents doing anything to a model
    """

    actions = None


class DeleteOnlyModelAdminBase(
    CannotAddModelAdminBase, CannotUpdateModelAdminBase,
    CannotEditModelAdminBase
):
    """"
    Prevents doing anything to a model, except for deletion
    """

    pass


#################
# normal admins #
#################


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

@admin.register(AstrosatSettings)
class AstrosatSettingsAdmin(admin.ModelAdmin):
    pass


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

        fields_to_export = ["id", "uuid", "level", "created", "message", "tags"]

        csv_response = HttpResponse(content_type="text/csv")
        csv_response["Content-Disposition"] = f"attachment; filename=log_records.csv"

        writer = csv.writer(csv_response)
        writer.writerow(fields_to_export)
        for data in DatabaseLogRecordSerializer(queryset, many=True).data:
            row = [data[field] for field in fields_to_export]  # doing this manually to preserve order
            writer.writerow(row)

        return csv_response

    export_as_csv.short_description = "Export selected Log Records as CSV"
