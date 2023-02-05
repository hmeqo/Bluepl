import typing as _t

try:
    from .validators import ValidatorsType, ValidatorType
except ImportError:
    from validators import ValidatorsType, ValidatorType


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

    def parse(self, value):
        if value is None:
            if self.nullable:
                return None
            elif self.default is not None:
                value = self.default
        if isinstance(value, self._type) and all(f(value) for f in self.validators):
            return value
        raise ValueError(value)

    @property
    def type(self):
        return self._type


class Form(object):

    def __init__(self, items: _t.Optional[_t.Dict[str, Field]] = None, **kwds: Field):
        if items:
            kwds.update(items)
        self.items = kwds

    def validate(self, items: dict):
        if set(items).difference(self.items):
            return False
        return all(item.validate(items.get(k)) for k, item in self.items.items())

    def parse(self, items: dict):
        result = {}
        try:
            for name, field in self.items.items():
                result[name] = field.parse(items.get(name))
        except ValueError:
            return None
        return result


def main():
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
    # print(form.validate({"username": "", "password": "123"}))


if __name__ == "__main__":
    main()
