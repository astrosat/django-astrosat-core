from django.db.models import CASCADE


def CONDITIONAL_CASCADE(collector, field, sub_objs, using, **kwargs):
    """
    Django deletion constraint that is a combination of CASCADE and SET.
    If condition (which is a dict of lookup arguemnts) is True then CASCADE
    is used, otherwise SET(default_value) is used.

    "condition" & "default_value" can be provided via `functools.partial` like this:
    ```
    my_field = models.ForeignKey(
      my_thing,
      on_delete=functools.partial(
          CONDITIONAL_CASCADE,
          condition={"some_lookup_arg": "some_value"},
          default_value=None,
      )
    )
    ```
    """

    condition = kwargs["condition"]
    default_value = kwargs.get("default_value", None)

    sub_objs_to_cascade = sub_objs.filter(**condition)
    sub_objs_to_set_null = sub_objs.exclude(**condition)

    CASCADE(collector, field, sub_objs_to_cascade, using)
    collector.add_field_update(field, default_value, sub_objs_to_set_null)


def bulk_update_or_create(model_class, model_data, comparator_fn=None):
    """
    Performs update_or_create in bulk (w/ only 3 db hits)
    Parameters
    ----------
    model_class : django.db.models.Model
        model to update_or_create
    model_data : list
        data to update/create.  Example: [{'field1': 'value', 'field2': 'value'}, ...]
    comparator_fn: function
        a function that compares a model instance w/ model data to determine if it needs to be updated
    Returns
    -------
    tuple
        the number of objects created & updated
    """

    # get all instances of the model...
    existing_objects = list(model_class.objects.all())

    # get all the fields that uniquely identify a model object...
    # TODO: deal w/ unique_together fields
    unique_field_names = [
        field.name for field in model_class._meta.get_fields()
        if field.concrete and not field.primary_key and field.unique
    ]
    all_data_record_field_names = set()

    objects_to_create = []
    objects_to_update = []

    for data_record in model_data:

        # for every dictionary in model_data,
        # extract the fields that can uniquely identify an object,
        # and check if there is an existing object w/ those values,
        # if so (and if the comparator_fn fails) update that object w/ the field values and store it to be UPDATED,
        # then remove it from the list of existing objects (so the next time around the check is faster),
        # if not store it to be CREATED

        all_data_record_field_names.update(data_record.keys())
        unique_data_record_fields = {
            # raises a KeyError if data doesn't include unique_fields
            field_name: data_record[field_name]
            for field_name in unique_field_names
        }

        matching_object = next(
            (
                obj for obj in existing_objects if all([
                    getattr(obj, k) == v for k,
                    v in unique_data_record_fields.items()
                ])
            ),
            None,
        )
        if matching_object:
            if comparator_fn is None or not comparator_fn(
                matching_object, data_record
            ):
                for k, v in data_record.items():
                    setattr(matching_object, k, v() if callable(v) else v)
                objects_to_update.append(matching_object)
            existing_objects.remove(matching_object)
        else:
            objects_to_create.append(model_class(**data_record))

    all_data_record_field_names.remove(*unique_field_names)

    model_class.objects.bulk_create(objects_to_create)
    model_class.objects.bulk_update(
        objects_to_update, all_data_record_field_names
    )

    # returns a tuple of created objects & updated objects
    return (objects_to_create, objects_to_update)
