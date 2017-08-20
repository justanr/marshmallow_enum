import sys
from collections import namedtuple
from enum import Enum

import pytest
from marshmallow import Schema, ValidationError
from marshmallow.fields import List
from marshmallow_enum import EnumField

PY2 = sys.version_info.major == 2


class EnumTester(Enum):
    one = 1
    two = 2
    three = 3


SomeObj = namedtuple('SingleEnum', ['enum'])


class TestEnumFieldByName(object):

    def setup(self):
        self.field = EnumField(EnumTester)

    def test_serialize_enum(self):
        assert self.field._serialize(EnumTester.one, None, object()) == 'one'

    def test_serialize_none(self):
        assert self.field._serialize(None, None, object()) is None

    def test_deserialize_enum(self):
        assert self.field._deserialize('one', None, {}) == EnumTester.one

    def test_deserialize_none(self):
        assert self.field._deserialize(None, None, {}) is None

    def test_deserialize_nonexistent_member(self):
        with pytest.raises(ValidationError):
            self.field._deserialize('fred', None, {})


class TestEnumFieldValue(object):

    def test_deserialize_enum(self):
        field = EnumField(EnumTester, by_value=True)

        assert field._deserialize(1, None, {}) == EnumTester.one

    def test_serialize_enum(self):
        field = EnumField(EnumTester, by_value=True)
        assert field._serialize(EnumTester.one, None, object()) == 1

    def test_serialize_none(self):
        field = EnumField(EnumTester, by_value=True)
        assert field._serialize(None, None, object()) is None

    def test_deserialize_nonexistent_member(self):
        field = EnumField(EnumTester, by_value=True)

        with pytest.raises(ValidationError):
            field._deserialize(4, None, {})


class TestEnumFieldAsSchemaMember(object):

    class EnumSchema(Schema):
        enum = EnumField(EnumTester)
        none = EnumField(EnumTester)

    def test_enum_field_load(self):
        serializer = self.EnumSchema()
        data = serializer.load({'enum': 'one', 'none': None}).data

        assert data['enum'] == EnumTester.one

    def test_enum_field_dump(self):
        serializer = self.EnumSchema()
        data = serializer.dump(SomeObj(EnumTester.one)).data

        assert data['enum'] == 'one'


class TestEnumByValueAsSchemaMember(object):

    class EnumSchema(Schema):
        enum = EnumField(EnumTester, by_value=True)
        none = EnumField(EnumTester, by_value=True)

    def test_enum_field_load(self):
        serializer = self.EnumSchema()
        data = serializer.load({'enum': 1, 'none': None}).data

        assert data['enum'] == EnumTester.one

    def test_enum_field_dump(self):
        serializer = self.EnumSchema()
        data = serializer.dump(SomeObj(EnumTester.one)).data

        assert data['enum'] == 1


class TestEnumFieldInListField(object):

    class ListEnumSchema(Schema):
        enum = List(EnumField(EnumTester))

    def test_enum_list_load(self):
        serializer = self.ListEnumSchema()
        data = serializer.load({'enum': ['one', 'two']}).data

        assert data['enum'] == [EnumTester.one, EnumTester.two]

    def test_enum_list_dump(self):
        serializer = self.ListEnumSchema()
        data = serializer.dump(SomeObj([EnumTester.one, EnumTester.two])).data

        assert data['enum'] == ['one', 'two']


class TestEnumFieldByValueInListField(object):

    class ListEnumSchema(Schema):
        enum = List(EnumField(EnumTester, by_value=True))

    def test_enum_list_load(self):
        serializer = self.ListEnumSchema()
        data = serializer.load({'enum': [1, 2]}).data

        assert data['enum'] == [EnumTester.one, EnumTester.two]

    def test_enum_list_dump(self):
        serializer = self.ListEnumSchema()
        data = serializer.dump(SomeObj([EnumTester.one, EnumTester.two])).data

        assert data['enum'] == [1, 2]


class TestCustomErrorMessage(object):

    def test_custom_error_in_deserialize_by_value(self):
        field = EnumField(EnumTester, by_value=True, error="{input} must be one of {choices}")
        with pytest.raises(ValidationError) as excinfo:
            field._deserialize(4, None, {})

        expected = "4 must be one of 1, 2, 3"
        assert expected in str(excinfo.value)

    def test_custom_error_in_deserialize_by_name(self):
        field = EnumField(EnumTester, error="{input} must be one of {choices}")
        with pytest.raises(ValidationError) as excinfo:
            field._deserialize('four', None, {})
        expected = 'four must be one of one, two, three'
        assert expected in str(excinfo)

    def test_uses_default_error_if_no_custom_provided(self):
        field = EnumField(EnumTester, by_value=True)
        with pytest.raises(ValidationError) as excinfo:
            field._deserialize(4, None, {})
        expected = 'Invalid enum value 4'
        assert expected in str(excinfo.value)


class TestRegressions(object):

    @pytest.mark.parametrize('bad_value', [object, object(), [], {}, 1, 3.4, False, ()])
    def test_by_name_must_be_string(self, bad_value):

        class SomeEnum(Enum):
            red = 0
            yellow = 1
            green = 2

        class SomeSchema(Schema):
            colors = EnumField(
                SomeEnum,
                by_value=False,
            )

        with pytest.raises(ValidationError) as excinfo:
            SomeSchema(strict=True).load({'colors': bad_value})

        assert 'must be string' in str(excinfo.value)

    @pytest.mark.skipif(PY2, reason='py2 strings are bytes')
    def test_by_name_cannot_be_bytes(self):

        class SomeEnum(Enum):
            a = 1

        class SomeSchema(Schema):
            f = EnumField(SomeEnum, by_value=False)

        with pytest.raises(ValidationError) as excinfo:
            SomeSchema(strict=True).load({'f': b'a'})

        assert 'must be string' in str(excinfo.value)


class TestLoadDumpConfigBehavior(object):

    def test_load_and_dump_by_default_to_by_value(self):
        f = EnumField(EnumTester)
        assert f.load_by == EnumField.NAME
        assert f.dump_by == EnumField.NAME

    def test_load_by_raises_if_not_proper_value(self):
        with pytest.raises(ValueError) as excinfo:
            EnumField(EnumTester, load_by='lol')

        assert 'Invalid selection' in str(excinfo.value)

    def test_dump_by_raises_if_not_proper_value(self):
        with pytest.raises(ValueError) as excinfo:
            EnumField(EnumTester, dump_by='lol')

        assert 'Invalid selection' in str(excinfo.value)

    def test_dumps_to_value_when_configured_to(self):

        class SomeSchema(Schema):
            f = EnumField(EnumTester, dump_by=EnumField.VALUE)

        expected = {'f': 1}
        actual = SomeSchema().dump({'f': EnumTester.one}).data
        assert expected == actual

    def test_loads_to_value_when_configured_to(self):

        class SomeSchema(Schema):
            f = EnumField(EnumTester, load_by=EnumField.VALUE)

        expected = {'f': EnumTester.one}
        actual = SomeSchema().load({'f': 1}).data
        assert expected == actual

    def test_load_by_value_dump_by_name(self):

        class SomeSchema(Schema):
            f = EnumField(EnumTester, load_by=EnumField.VALUE, dump_by=EnumField.NAME)

        schema = SomeSchema()

        expected = {'f': 'one'}
        actual = schema.dump(schema.load({'f': 1}).data).data
        assert actual == expected

    def test_load_by_name_dump_by_value(self):

        class SomeSchema(Schema):
            f = EnumField(EnumTester, load_by=EnumField.NAME, dump_by=EnumField.VALUE)

        schema = SomeSchema()
        expected = {'f': 1}
        actual = schema.dump(schema.load({'f': 'one'}).data).data
        assert actual == expected
