import importlib

from django.apps import apps
from django.conf import LazySettings
from django.core.exceptions import AppRegistryNotReady, ImproperlyConfigured
from django.utils.functional import LazyObject, empty


class DynamicSetting(object):
    """
    Allows a variable in DJANGO_SETTINGS_MODULE to be defined by a field in a SingletonMixin.
    Therefore, it can be used before any apps have been loaded.
    Note that this is a standard Python Class, rather than a Django Model.
    """

    def __init__(self, source, default_value):
        """
        Defines a settings variable as dynamic.  Usage is:
        >>> MY_SETTING = DynamicSetting("my_app.MyModel.my_setting", default=False)
        This will try to assign the value of my_app.MyModel.my_setting (which must be a singleton) to MY_SETTING.
        If anything goes wrong, it will fall back to the default value.
        """
        if len(source.split(".")) != 3:
            msg = f"Invalid DynamicSetting value; format is <app>.<model>.<attr>"
            raise ImproperlyConfigured(msg)
        self.source = source
        self.default_value = default_value

    @property
    def value(self):
        app_name, model_name, attr_name = self.source.split(".")
        try:
            model = apps.get_model(app_label=app_name, model_name=model_name)
            # model is a SingletonMixin, so pk will always equal 1
            instance, created = model.objects.get_or_create(pk=1)
            attr = getattr(instance, attr_name)
            if created and attr != self.default_value:
                attr = self.default_value
                setattr(instance, attr_name, attr)
                instance.save()
            return attr
        except AppRegistryNotReady:
            return self.default_value

    @classmethod
    def configure(cls):
        """
        Called once this app (and therefore, the django.conf app) is loaded.
        Patches the LazySettings.__getattr__ w/ a custom fn which checks to
        see if the attr is an instance of a DynamicSetting; if so, it returns
        the current value from the db.
        """

        def _new_getattr(instance, name):
            if instance._wrapped is empty:
                instance._setup(name)
            attr = getattr(instance._wrapped, name)
            if isinstance(attr, DynamicSetting):
                # if the attr is dynamic, return its computed value
                return attr.value
            instance.__dict__[name] = attr
            return attr

        # TODO: NOT SURE WHY USING TYPES DOESN'T WORK
        # setattr(LazySettings, "__getattr__", types.MethodType(_new_getattr, LazySettings))
        setattr(LazySettings, "__getattr__", _new_getattr)


class DynamicAppSettings(LazyObject):
    """
    Allows app_settings to use DynamicSetting instances above.
    Usage is:
    >
    > my_app/conf/__init__.py:
    >  from astrosat.utils import DynamicAppSettings
    >  app_settings = DynamicAppSettings("my_app.conf.app_settings")
    >
    > app/conf/app_settings.py:
    >  from django.conf import settings
    >  from astrosat.utils import DynamicSettings
    >  MY_SETTING = getattr(settings, "MY_SETTING", DynamicSetting("my_app.my_model.my_setting, default_value))
    """

    # this is a bare-bones implementation of Django's LazySetting class

    def __init__(self, module):
        self._wrapped = empty
        self._module = module

    def __getattr__(self, name):

        if name == "_module":
            return self._module

        if self._wrapped is empty:
            self._setup()

        attr = self._wrapped[name]
        if isinstance(attr, DynamicSetting):
            # if the setting is Dynamic, get its value from the db
            return attr.value

        return attr

    def __setattr__(self, name, value):

        if name in ["_wrapped", "_module"]:
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__[name] = value
        else:
            if self._wrapped is empty:
                self._setup()
            self._wrapped[name] = value

    def _setup(self):
        app_settings_module = importlib.import_module(self._module)
        self._wrapped = {
            app_setting: getattr(app_settings_module, app_setting)
            for app_setting in dir(app_settings_module)
            if app_setting.isupper()
        }


# class DynamicAppSettings(object):

#     """
#     Allows app_settings to use DynamicSetting instances above.
#     Usage is:
#     >
#     > my_app/conf/__init__.py:
#     >  from astrosat.utils import DynamicAppSettings
#     >  app_settings = DynamicAppSettings("my_app.conf.app_settings")
#     >
#     > app/conf/app_settings.py:
#     >  from django.conf import settings
#     >  from astrosat.utils import DynamicSettings
#     >  MY_SETTING = getattr(settings, "MY_SETTING", DynamicSetting("my_app.my_model.my_setting, default_value))
#     """

#     def __init__(self, module_name):
#         # Just like Django's LazySettings object,
#         # copies all settings into object.__dict__ for use later
#         app_settings_module = importlib.import_module(module_name)
#         for app_setting_name in dir(app_settings_module):
#             if app_setting_name.isupper():
#                 app_setting_value = getattr(app_settings_module, app_setting_name)
#                 setattr(self, app_setting_name, app_setting_value)

#     def __getattribute__(self, name):
#         attr = object.__getattribute__(self, name)
#         if isinstance(attr, DynamicSetting):
#             # if the setting is Dynamic, get its value from the db
#             return attr.value
#         return attr
