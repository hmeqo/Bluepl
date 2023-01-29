import typing as _t

ExpectValidator = _t.Callable[[_t.Any], bool]
ExpectValidators = _t.Union[ExpectValidator, _t.Iterable[ExpectValidator]]


class Validator(object):

    def __init__(self, func: ExpectValidator, **kwds):
        if isinstance(func, Validator):
            self.func: ExpectValidator = func.func
        else:
            self.func = func
        for k, v in kwds.items():
            setattr(self, k, v)

    def __call__(self, value):
        if self.func(value):
            self.on_valid(value)
            return True
        self.on_invalid(value)
        return False

    def on_valid(self, value):
        pass

    def on_invalid(self, value):
        pass


def required(**kwds):
    return Validator(lambda x: bool(x), **kwds)


def is_obj(obj, **kwds):
    return Validator(lambda x: x is obj, **kwds)


def is_not_obj(obj, **kwds):
    return Validator(lambda x: x is not obj, **kwds)


def equals(value, **kwds):
    return Validator(lambda x: x == value, **kwds)


def between(left, right, **kwds):
    return Validator(lambda x: left < x < right, **kwds)


def scope(left, right, **kwds):
    return Validator(lambda x: left <= x <= right, **kwds)
