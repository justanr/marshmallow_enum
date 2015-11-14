from marshmallow_enum import EnumField
from marshmallow import Schema, ValidationError
from marshmallow.fields import List
from enum import Enum
from collections import namedtuple
import pytest

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

    def test_deserialize_enum(self):
        assert self.field._deserialize('one', None, {}) == EnumTester.one

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

    def test_deserialize_nonexistent_member(self):
        field = EnumField(EnumTester, by_value=True)

        with pytest.raises(ValidationError):
            field._deserialize(4, None, {})

class TestEnumFieldAsSchemaMember(object):
    class EnumSchema(Schema):
        enum = EnumField(EnumTester)

    def test_enum_field_load(self):
        serializer = self.EnumSchema()
        data = serializer.load({'enum': 'one'}).data

        assert data['enum'] == EnumTester.one

    def test_enum_field_dump(self):
        serializer = self.EnumSchema()
        data = serializer.dump(SomeObj(EnumTester.one)).data

        assert data['enum'] == 'one'


class TestEnumByValueAsSchemaMember(object):
    class EnumSchema(Schema):
        enum = EnumField(EnumTester, by_value=True)

    def test_enum_field_load(self):
        serializer = self.EnumSchema()
        data = serializer.load({'enum': 1}).data

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
