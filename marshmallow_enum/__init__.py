from marshmallow.fields import Field
from marshmallow import ValidationError

try:
    # ugh Python 2
    str_types = (str, unicode)
except:
    str_types = (str,)


class EnumField(Field):
    default_error_messages = {
        'by_name': 'Invalid enum member {input}',
        'by_value': 'Invalid enum value {input}',
        'must_be_string': 'Enum name must be string'
    }

    def __init__(self, enum, by_value=False, error='',  *args, **kwargs):
        self.enum = enum
        self.by_value = by_value
        self.error = error
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
        except ValueError:
            self.fail('by_value', input=value)

    def _deserialize_by_name(self, value, attr, data):
        if not isinstance(value, str_types):
            self.fail('must_be_string', input=value)

        try:
            return getattr(self.enum, value)
        except AttributeError:
            self.fail('by_name', input=value)

    def fail(self, key, **kwargs):
        # depercation of name/value fail inputs
        if 'name' in kwargs:
            kwargs['input'] = kwargs['name']
        elif 'value' in kwargs:
            kwargs['input'] = kwargs['value']

        if self.error:
            if self.by_value:
                kwargs['choices'] = ', '.join([str(mem.value) for mem in self.enum])
            else:
                kwargs['choices'] = ', '.join([mem.name for mem in self.enum])
            msg = self.error.format(**kwargs)
            raise ValidationError(msg)
        else:
            super(EnumField, self).fail(key, **kwargs)
