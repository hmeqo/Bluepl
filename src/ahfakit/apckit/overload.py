"""Javalike overload and typechecker

Usage:
```
@Overload
def func():
    pass
@func.overload
def func(a: int):
    pass
class Test:
    @Overload.from_method
    def method():
        pass
```
"""

from typing import Callable, Optional, TypeVar


class Overload(property):
    """Like the java overload."""

    def __init__(self, func: Optional[Callable] = None, self_flag=False):
        super().__init__()
        self.functions: list[TypeChecker] = []
        self.self_flag = self_flag
        if func is not None:
            self.functions.append(TypeChecker(func))

    def __call__(self, *args, **kwargs):
        for typechecker in self.functions:
            if typechecker.check(args, kwargs):
                return typechecker.func(*args, **kwargs)
        raise ValueError

    def __get__(self, obj, type=...):
        return lambda *args, **kwargs: self._arg_wrapper(obj, args, kwargs)

    def __set__(self, instance, value):
        raise Exception

    def __delete__(self, instance):
        raise Exception

    def _arg_wrapper(self, instance, args: tuple, kwargs: dict):
        if self.self_flag:
            args = (instance,) + args
        for typechecker in self.functions:
            if typechecker.check(args, kwargs):
                return typechecker.func(*args, **kwargs)
        raise ValueError

    @classmethod
    def from_method(cls, func):
        return cls(func, self_flag=True)

    def overload(self, func: Callable):
        self.functions.append(TypeChecker(func))
        return self


class TypeChecker(object):
    """Check arguments type, not supported for mutable args.

    It is can be used like decorator.
    """

    def __init__(self, func: Callable):
        kw = dict.fromkeys(func.__code__.co_varnames, object)
        kw.update(filter(lambda x: x[0] != "return",
                         func.__annotations__.items()))
        pac = (func.__code__.co_argcount - func.__code__.co_kwonlyargcount)
        varnames = func.__code__.co_varnames
        self.func = func
        self.typehint_args = {i: kw[i] for i in varnames[:pac]}
        self.typehint_kwds = {i: kw[i] for i in varnames[pac:]}

    def __call__(self, *args, **kwds):
        if self.check(args, kwds):
            return self.func(*args, **kwds)
        raise ValueError

    def check(self, args: tuple, kwargs: dict):
        """Check arguments"""
        if len(args) <= len(self.typehint_args):
            a = tuple(self.typehint_args.items())
            a1 = a[:len(args)]
            arg_flag = all(isinstance(obj, j[1]) for obj, j in zip(args, a1))
            a2 = dict(a[len(args):])
            a2.update(self.typehint_kwds)
            kwa = kwargs.copy()
            kw_flag = all(name in kwa and isinstance(kwa.pop(name), type_)
                          for name, type_ in a2.items()) and not kwa
            if arg_flag and kw_flag:
                return True
        return False


def main():
    class A(object):

        @Overload.from_method
        def get(self):
            return "Hello World"

        @get.overload
        def get(self, a: int, b: int):
            return a + b

    a = A()
    print(a.get())
    print(a.get(1, 2))

    @TypeChecker
    def test():
        pass


if __name__ == "__main__":
    main()
