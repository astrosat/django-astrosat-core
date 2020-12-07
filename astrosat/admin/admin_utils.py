import json

from django.contrib import admin
from django.forms import widgets
from django.urls import resolve, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


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
        self.empty_value_display = model_admin.get_empty_value_display()

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
            # need to work on a copy so I don't change it for other lookup_choices in the generator below
            selections = self.lookup_val.copy()
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
                'display': self.empty_value_display,
            }
