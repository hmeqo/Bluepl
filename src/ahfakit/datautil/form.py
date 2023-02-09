"""
Usage:

```
from validators import required, equals
form = Form(
    username=Field(str, validator=[
        required(on_invalid=lambda v: print("不能为空")),
        equals("abc", on_invalid=lambda v: print("账号错误")),
    ]),
    password=Field(str, equals("123")),
    test=Field(str, ""),
)
print(form.parse({"username": "abc", "password": "123"}))
```
"""

from __future__ import annotations
import typing as _t

from .validators import ValidatorsType, ValidatorType


class Field(object):

    ExpectType = _t.Union[type, _t.Tuple[type, ...]]

    def __init__(
        self,
        type: ExpectType,
        default=None,
        nullable=False,
        validator: _t.Optional[ValidatorsType] = None,
    ):
        self.validators: _t.List[ValidatorType] = []
        if validator is not None:
            if isinstance(validator, _t.Iterable):
                self.validators.extend(validator)
            else:
                self.validators.append(validator)
        self.default = default
        self.nullable = nullable
        self._type = type

    def validate(self, value):
        if value is None:
            if self.nullable:
                return True
            elif self.default:
                value = self.default
        return isinstance(value, self._type) and all(f(value) for f in self.validators)

    def parse(self, value, ignore_error=False):
        if value is None:
            if self.nullable:
                return None
            elif self.default is not None:
                value = self.default
        if isinstance(value, self._type) and all(f(value) for f in self.validators):
            return value
        if not ignore_error:
            raise ValueError(value)

    @property
    def type(self):
        return self._type


class Form(object):

    def validate(self, items: _t.Optional[_t.Any] = None) -> bool:
        raise NotImplementedError

    def parse(self, items: _t.Optional[_t.Any] = None, ignore_error=True) -> _t.Any:
        raise NotImplementedError


class DictForm(Form):

    def __init__(self, fields: _t.Optional[FieldDict] = None, **kwds: ExpectField):
        if fields:
            kwds.update(fields)
        self.fields = kwds

    def validate(self, items: _t.Optional[dict] = None):
        if not isinstance(items, dict):
            return False
        if set(items).difference(self.fields):
            return False
        return all(item.validate(items.get(k)) for k, item in self.fields.items())

    def parse(self, items: _t.Optional[dict] = None, ignore_error=True):
        try:
            if not isinstance(items, dict):
                raise ValueError
            return {
                name: field.parse(items.get(name), ignore_error=False)
                for name, field in self.fields.items()
            }
        except ValueError as e:
            if ignore_error:
                return None
            raise e


class ListForm(Form):

    def __init__(self, field: ExpectField):
        self.field = field

    def validate(self, items: _t.Optional[list] = None):
        if not isinstance(items, list):
            return False
        return all(self.field.validate(i) for i in items)

    def parse(self, items: _t.Optional[list] = None, ignore_error=True):
        try:
            if not isinstance(items, list):
                raise ValueError
            return [self.field.parse(i, ignore_error=False) for i in items]
        except ValueError as e:
            if ignore_error:
                return None
            raise e


ExpectField = _t.Union[Field, DictForm, ListForm]

FieldDict = _t.Dict[str, ExpectField]

FieldList = _t.List[ExpectField]
