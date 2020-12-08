import json
from itertools import filterfalse

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

    # include_empty_choice = True
    parameter_name = None
    template = 'astrosat/admin/include_exclude_filter.html'
    title = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.lookup_expr_in = f"{self.parameter_name}__in"
        self.lookup_expr_out = f"{self.parameter_name}__out"
        self.lookup_expr_eq = f"{self.parameter_name}__eq"
        # notice that I use `pop` instead of `get` - this ensures
        # that non-registered lookup_expr (like "__out" or "__eq") don't
        # get passed onto any parent methods
        _lookup_val_in = params.get(self.lookup_expr_in, [])
        _lookup_val_out = params.pop(self.lookup_expr_out, [])
        _lookup_val_eq = params.pop(self.lookup_expr_eq, None)
        self.lookup_val_in = _lookup_val_in.split(",") if _lookup_val_in else []
        self.lookup_val_out = _lookup_val_out.split(","
                                                   ) if _lookup_val_out else []
        self.lookup_val_eq = _lookup_val_eq

    def lookups(self, request, model_admin):
        raise NotImplementedError()

    def queryset(self, request, queryset):
        if self.lookup_val_in:
            queryset = queryset.filter(
                **{self.lookup_expr_in: self.lookup_val_in}
            )
        if self.lookup_val_out:
            queryset = queryset.exclude(
                **{self.lookup_expr_in: self.lookup_val_out}
            )
        return queryset

    def choices(self, changelist):

        lookup_val_eq = self.lookup_val_eq
I AM HERE; THIS NEARLY WORKS
        def _get_query_string(include=None, exclude=None):
            # need to work on a copy so I don't change it for other lookup_choices in the generator below
            selections_in = self.lookup_val_in.copy()
            selections_out = self.lookup_val_out.copy()
            if include and include not in selections_in:
                selections_in.append(include)
            if exclude and exclude not in selections_out:
                selections_out.append(exclude)
            if lookup_val_eq == "in":
                selections_out = filterfalse(
                    lambda x: x in selections_in, selections_out
                )
            elif lookup_val_eq == "out":
                selections_in = filterfalse(
                    lambda x: x in selections_out, selections_in
                )

            query_args = {}
            query_remove = []
            if selections_in:
                query_args[self.lookup_expr_in] = ",".join(selections_in)
            else:
                query_remove.append(self.lookup_expr_in)
            if selections_out:
                query_args[self.lookup_expr_out] = ",".join(selections_out)
            else:
                query_remove.append(self.lookup_expr_out)

            if include is not None:
                query_args[self.lookup_expr_eq] = "in"
            elif exclude is not None:
                query_args[self.lookup_expr_eq] = "out"

            return changelist.get_query_string(query_args, remove=query_remove)

        yield {
            'selected':
                not self.lookup_val_in and not self.lookup_val_out,
            'query_string':
                changelist.get_query_string(
                    remove=[self.lookup_expr_in, self.lookup_expr_out]
                ),
            'display':
                _('Any'),
        }

        for lookup, val in self.lookup_choices:
            yield {
                "selected_in": str(lookup) in self.lookup_val_in,
                "selected_out": str(lookup) in self.lookup_val_out,
                # 'query_string': changelist.get_query_string({self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]),
                "include_query_string": _get_query_string(include=str(lookup)),
                "exclude_query_string": _get_query_string(exclude=str(lookup)),
                "display": val,
            }
        # if self.include_empty_choice:
        #     yield {
        #         'selected': bool(self.lookup_val_isnull),
        #         'query_string': changelist.get_query_string({self.lookup_kwarg_isnull: True}, [self.lookup_kwarg]),
        #         'display': self.empty_value_display,
        #     }
