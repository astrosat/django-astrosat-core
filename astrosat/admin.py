from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.utils import flatten_fieldsets
from django.urls import resolve, reverse
from django.utils.html import format_html

from .models import AstrosatSettings


############
# util fns #
############


def get_clickable_m2m_list_display(model_class, queryset):
    """
    Prints a pretty (clickable) representation of a m2m field for an Admin's `list_display`.
    Note that when using this it is recommended to call `prefetch_related` in the Admin's
    `get_queryset` fn in order to avoid the "n+1" problem.
    """
    list_display = [
        f"<a href='{reverse(f'admin:{model_class._meta.db_table}_change', args=[obj.id])}'>{str(obj)}</a>"
        for obj in queryset
    ]
    return format_html(", ".join(list_display))


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

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):

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
                [f.name for f in self.opts.local_fields]
                + [f.name for f in self.opts.local_many_to_many]
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
    CannotAddModelAdminBase, CannotUpdateModelAdminBase, CannotEditModelAdminBase
):

    """"
    Prevents doing anything to a model, except for deletion
    """

    pass


#################
# normal admins #
#################


@admin.register(AstrosatSettings)
class AstrosatSettingsAdmin(admin.ModelAdmin):
    pass
