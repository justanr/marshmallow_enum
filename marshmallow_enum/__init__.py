from marshmallow.fields import Field
from marshmallow.exceptions import ValidationError


class EnumField(Field):
    default_error_messages = {
        'by_name': 'Invalid enum member {name}',
        'by_value': 'Invalid enum value {value}'
    }

    def __init__(self, enum, by_value=False, *args, **kwargs):
        self.enum = enum
        self.by_value = by_value
        super(EnumField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        elif self.by_value:
            return value.value
        else:
            return value.name

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        elif self.by_value:
            return self._deserialize_by_value(value, attr, data)
        else:
            return self._deserialize_by_name(value, attr, data)

    def _deserialize_by_value(self, value, attr, data):
        try:
            return self.enum(value)
        except ValueError as e:
            self.fail('by_value', value=value)

    def _deserialize_by_name(self, value, attr, data):
        try:
            return getattr(self.enum, value)
        except AttributeError as e:
            self.fail('by_name', name=value)
