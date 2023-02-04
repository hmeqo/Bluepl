import typing as _t

from .validators import *


class Field(object):

    ExpectType = _t.Union[type, _t.Tuple[type, ...]]

    def __init__(self, type: ExpectType, validator: _t.Optional[ValidatorsType] = None):
        self.validators: _t.List[ValidatorType] = []
        if validator is not None:
            if isinstance(validator, _t.Iterable):
                self.validators.extend(validator)
            else:
                self.validators.append(validator)
        self._type = type

    def validate(self, value):
        return isinstance(value, self._type) and all(f(value) for f in self.validators)

    @property
    def type(self):
        return self._type


class Form(object):

    def __init__(self, **kwds: Field):
        self.items = kwds

    def validate(self, items: dict):
        if set(self.items).difference(items):
            return False
        return all(item.validate(items[k]) for k, item in self.items.items())


def main():
    form = Form(
        username=Field(str, [
            required(on_invalid=lambda: print("不能为空")),
            equals("abc", on_invalid=lambda: print("账号错误")),
        ]),
        password=Field(str, equals("123")),
    )
    print(form.validate({"username": "", "password": "123"}))


if __name__ == "__main__":
    main()
