from django.contrib import admin

from .models import (
    ExampleHashableModel,
    ExampleSingletonModel,
    ExampleBulkModel,
    ExampleEpochModel,
    ExampleUnloadableParentModel,
    ExampleUnloadableChildModel,
    ExampleConditionallyDeletedThing,
    ExampleMediaModel,
)

admin.site.register(ExampleHashableModel)
admin.site.register(ExampleSingletonModel)
admin.site.register(ExampleBulkModel)
admin.site.register(ExampleEpochModel)
admin.site.register(ExampleUnloadableParentModel)
admin.site.register(ExampleUnloadableChildModel)
admin.site.register(ExampleConditionallyDeletedThing)
admin.site.register(ExampleMediaModel)
