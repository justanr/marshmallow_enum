# marshmallow-enum

Enum serializer/deserializer for use with Marshmallow.

Making use of the field is straightforward, it does depend on an existing Enum. By default, the field will serialize and deserialize based on the *names* in Enum:

```python
from marshmallow import Schema, post_load
from marshmallow_enum import EnumField
from enum import Enum


class PermissionEnum(Enum):
    guest = 0
    member = 1
    admin = 2
    
    
class UserSchema(Schema):
    permission_level = EnumField(PermissionEnum)
    
    class Meta:
        additional = ['username']
        
    @post_load
    def make_user(self, data):
        return User(**data)

print(UserSchema().dump(User(username='justanr', permission_level=PermissionEnum.admin)).data)
# {'username': 'justanr', 'permission_level': 'admin'}

print(UserSchema().load({'username': 'justanr', 'permission_level': 'admin'}).data)
# User(username='justanr', permission_level=<PermissionEnum.admin: 2>)
```

Alternatively, you can choose to serialize or deserialize based on a *value* in the Enum as well:

```python
class UserSchema(Schema):
    permission_level = EnumField(PermissionEnum, by_value=True)
    
    class Meta:
        additional = ['username']
        
print(UserSchema().dump(User(username='justanr', permission_level=PermissionEnum.admin)).data)
# {'username': 'justanr', 'permission_level': 2}

print(UserSchema().load({'username': 'justanr', 'permission_level': 2}).data)
# User(username='justanr', permission_level=<PermissionEnum.admin: 2>)
```

Additionally, if you need to translate between two APIs -- for example an external API that provides some data in integers that actually represent something else, and repackaging it for use in your code -- you can make use of the `pre_load` and `pre_dump` mechanisms to do something a little scary:

```python
from marshmallow import pre_load, pre_dump, post_load

class UserSchema(Schema):
    permission_level = EnumField(PermissionEnum)
    
    class Meta:
        additional = ['username']
    
    @post_load
    def make_user(self, data):
        return User(**data)
    
    @pre_load(pass_many=True)
    def adjust_enum_load(self, data, *_):
        if not (self.context and 'source' in self.context):
            raise MarshmallowError('Must provide source in context dict')
        self.fields['permission_level'].by_value = self.context['source'] == 'external'
        return data
        
    @pre_dump(pass_many=True)
    def adjust_enum_dump(self, data, *_):
        if not (self.context and 'source' in self.context):
            raise MarshmallowError('Must provide source in context dict')
        self.fields['permission_level'].by_value = self.context['source'] == 'internal'
        return data

load_from_external = UserSchema(context={'source': 'external'})
print(load_from_external.load({'username': 'justanr', 'permission_level': 2}).data)
# User(username='justanr', permission_level=<PermissionEnum.admin: 2>)
print(load_from_external.dump(User(username='justanr', permission_level=PermissionEnum.admin).data)
# {'username': 'justanr', 'permission_level': 'admin'}

load_from_internal = UserSchema(context={'source': 'internal'})
print(load_from_internal.load({'username': 'justanr', 'permission_level': 'admin'}).data)
# User(username='justanr', permission_level=<PermissionEnum.admin: 2>)
print(load_from_internal.dump(User(username='justanr', permission_level=PermissionEnum.admin).data)
# {'username': 'justanr', 'permission_level': 2}
```

