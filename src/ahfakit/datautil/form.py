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

    def parse(self, value) -> _t.Tuple[bool, _t.Any]:
        if value is None:
            if self.nullable:
                return True, None
            elif self.default is not None:
                value = self.default
        if isinstance(value, self._type) and all(f(value) for f in self.validators):
            return True, value
        return False, None

    @property
    def type(self):
        return self._type


class Form(object):

    def validate(self, items: _t.Optional[_t.Any] = None) -> bool:
        raise NotImplementedError

    def parse(self, items: _t.Optional[_t.Any] = None) -> _t.Tuple[bool, _t.Any]:
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

    def parse(self, items: _t.Optional[dict] = None) -> _t.Tuple[bool, _t.Dict[str, _t.Any]]:
        results = {}
        if not isinstance(items, dict):
            return False, results
        for name, field in self.fields.items():
            success, result = field.parse(items.get(name))
            if not success:
                return False, results
            results[name] = result
        return True, results


class ListForm(Form):

    def __init__(self, field: ExpectField):
        self.field = field

    def validate(self, items: _t.Optional[list] = None):
        if not isinstance(items, list):
            return False
        return all(self.field.validate(i) for i in items)

    def parse(self, items: _t.Optional[list] = None) -> _t.Tuple[bool, _t.List[_t.Any]]:
        results = []
        if not isinstance(items, list):
            return False, results
        for i in items:
            success, result = self.field.parse(i)
            if not success:
                return False, results
            results.append(result)
        return True, results


ExpectField = _t.Union[Field, DictForm, ListForm]

FieldDict = _t.Dict[str, ExpectField]

FieldList = _t.List[ExpectField]
