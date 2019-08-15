from rest_framework import serializers


class LabelledHyperlinkedRelatedField(serializers.HyperlinkedRelatedField):
    """
    Just like the normal HyperlinkedRelatedField,
    but adds a label to the representation.
    """

    def __init__(self, view_name=None, **kwargs):
        self.always_show_label = kwargs.pop("always_show_label", False)
        return super().__init__(view_name=view_name, **kwargs)

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        if self.always_show_label or isinstance(self.parent, serializers.ManyRelatedField):
            return {str(obj): representation}
        return representation
