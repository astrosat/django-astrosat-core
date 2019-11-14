from rest_framework import serializers


class WritableNestedListSerializer(serializers.ListSerializer):
    """
    DRF doesn't have writeable nested serializers by default.  It is possible to
    overload update/create to cope w/ this.  But w/ ListSerializers you could only
    update models while updating the related model or only create models while creating
    the related model.  This class allows you to update and/or create models as needed.
    Typical usage is:

    >>> class MyRelatedSerializer(serializers.ModelSerializer):
    >>>     class Meta:
    >>>         model = RelatedModel
    >>>             fields = ("id", "some_other_field",)
    >>>             list_serializer_class = WritableNestedListSerializer

    >>> class MySerializer(serializers.ModelSerializer):
    >>>      class Meta:
    >>>          model = Model
    >>>          fields = ("id", "some_field", "related_models",)

    >>>      related_models = MyRelatedSerializer(many=True, required=False)

    >>>      def update(self, instance, validated_data):
    >>>          related_serializer = self.fields["related_models"]
    >>>          related_data = validated_data.pop(related_serializer.source)
    >>>          related_models = related_serializer.crud(
    >>>              instances=instance.related_models.all(),
    >>>              validated_data=related_data,
    >>>           )
    >>>           updated_instance = super().update(instance, validated_data)
    >>>           updated_instance.related_data.clear()
    >>>           updated_instance.related_data.add(*related_models)
    >>>           return updated_instance
    """

    def __init__(self, *args, **kwargs):
        """
        ensures that an id_field was provided for use w/ crud below
        """
        self.id_field = kwargs.get("id_field", "id")
        super().__init__(*args, **kwargs)
        assert (
            self.id_field in self.child.fields
        ), "WriteableNestedListSerializer requires a valid id field"

    def crud(self, instances=[], validated_data=[], delete_missing=False):

        models = []

        # map of existing instances...
        instance_mapping = {
            getattr(instance, self.id_field): instance for instance in instances
        }

        # map of instances specified in data...
        data_mapping = {
            data.get(self.id_field, id(data)): data for data in validated_data
        }

        # create every instance in data_mapping NOT in instance_mapping
        # update every instance in data_mapping AND in instance_mapping
        for model_id, model_data in data_mapping.items():
            model = instance_mapping.get(model_id, None)
            if model:
                models.append(self.child.update(model, model_data))
            else:
                models.append(self.child.create(model_data))

        # delete every instance in instance_mapping and NOT in data_mapping
        if delete_missing:
            for model_id, model in instance_mapping.items():
                model.delete()

        return models
