from __future__ import unicode_literals

import sys
import warnings

from marshmallow import ValidationError
from marshmallow.fields import Field

PY2 = sys.version_info.major == 2
# ugh Python 2
if PY2:
    string_types = (str, unicode)  # noqa: F821
    text_type = unicode  # noqa: F821
else:
    string_types = (str, )
    text_type = str


class EnumField(Field):
    default_error_messages = {
        'by_name': 'Invalid enum member {input}',
        'by_value': 'Invalid enum value {input}',
        'must_be_string': 'Enum name must be string'
    }

    def __init__(self, enum_type, by_value=True, error="", *args, **kwargs):
        self.enum = enum_type
        self.by_value = by_value

        if error and any(old in error for old in ('name}', 'value}', 'choices}')):
            warnings.warn(
                "'name', 'value', and 'choices' fail inputs are deprecated,"
                "use input, names and values instead",
                DeprecationWarning,
                stacklevel=2
            )

        self.error = error

        super(EnumField, self).__init__(*args, **kwargs)

        self.metadata['enum'] = [
            e.value if self.by_value else e.name
            for e in self.enum
        ]

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        elif self.by_value:
            return value.value
        else:
            return value.name

    def _deserialize(self, value, attr, data, **kwargs):
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
            self.fail('by_value', input=value, value=value)

    def _deserialize_by_name(self, value, attr, data):
        if not isinstance(value, string_types):
            self.fail('must_be_string', input=value, name=value)

        try:
            return getattr(self.enum, value)
        except AttributeError:
            self.fail('by_name', input=value, name=value)

    def fail(self, key, **kwargs):
        kwargs['values'] = ', '.join([text_type(mem.value) for mem in self.enum])
        kwargs['names'] = ', '.join([mem.name for mem in self.enum])

        if self.error:
            if self.by_value:
                kwargs['choices'] = kwargs['values']
            else:
                kwargs['choices'] = kwargs['names']
            msg = self.error.format(**kwargs)
            raise ValidationError(msg)
        else:
            super(EnumField, self).fail(key, **kwargs)
