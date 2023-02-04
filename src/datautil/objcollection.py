"""
Usage:

```
class MyObj(Obj):

    # name is "id", type is int, autoincrement
    id = AutoincObjProperty("id")
    # name is "name", type is str, nullable
    name = ObjProperty("name", (str, NONE_TYPE))
    # name is "age", type is int, default to 0
    age = ObjProperty("age", int, default=0)

collections = Collections()
myobjs = collections.get(MyObj)
myobjs.create(name="a")
myobjs.create(name="b")
myobjs.create(name="c")
print(myobjs)
```
"""

from __future__ import annotations
import os as _os
import tokenize as _tokenize
import typing as _t
import io as _io

from .validators import ValidatorType, ValidatorsType

AN_OBJECT = object()
NONE_TYPE = type(None)

ObjPropertyType = _t.TypeVar("ObjPropertyType")
WatcherType = _t.Callable[[_t.Any, _t.Any], None]


class MissingKeyError(Exception):
    pass


class ObjProperty(_t.Generic[ObjPropertyType]):
    """A property of Obj"""

    def __init__(
        self,
        name: str,
        type: _t.Union[_t.Type[ObjPropertyType], _t.Tuple[_t.Type[ObjPropertyType], ...]],
        default: _t.Optional[ObjPropertyType] = None,
        validator: _t.Optional[ValidatorsType] = None,
    ):
        self.name = name
        self.type = type
        self.default = default
        if isinstance(type, tuple):
            self.nullable = NONE_TYPE in type
        else:
            self.nullable = type is NONE_TYPE
        self.validators: _t.List[ValidatorType] = []
        if validator is not None:
            if isinstance(validator, _t.Iterable):
                self.validators.extend(validator)
            else:
                self.validators.append(validator)

    def __get__(self, instance: _t.Optional[Obj], obj_type: _t.Type[Obj]) -> ObjPropertyType:
        if instance is None:
            raise AttributeError
        value: _t.Any = instance.properties.get(self.name, AN_OBJECT)
        if value is AN_OBJECT:
            raise AttributeError
        return value

    def __set__(self, instance: Obj, value: _t.Optional[ObjPropertyType]):
        if value is None:
            # 判断有没有默认值
            if self.default is not None:
                value = self.default
            # 判断是否不允许为空
            elif not self.nullable:
                raise MissingKeyError(self.name)
        if not isinstance(value, self.type):
            raise TypeError(value)
        if not all(i(value) for i in self.validators):
            raise ValueError(value)
        instance.properties[self.name] = value


class Autoincrement(object):

    def __init__(self, current=0):
        self.current = current

    def next(self):
        self.current += 1
        return self.current


class AutoincObjProperty(ObjProperty, _t.Generic[ObjPropertyType]):
    """Autoincrement ObjProperty"""
    
    def __init__(self, name: str, init=1, increment=1):
        super().__init__(name, int)
        self.init = init
        self.increment = increment
        self.current = init - 1

    def __set__(self, instance: Obj, value: _t.Optional[ObjPropertyType]):
        if isinstance(value, int):
            self.current = value
            super().__set__(instance, value)
        else:
            super().__set__(instance, self._next())

    def _next(self):
        self.current += 1
        return self.current


class ObjMeta(type):

    def __init__(cls, name: str, bases: _t.Tuple[type], attr: dict):
        cls.name2property = {
            value.name: value
            for class_ in reversed(cls.mro())
            for value in class_.__dict__.values()
            if isinstance(value, ObjProperty)
        }


class Obj(metaclass=ObjMeta):
    """Object"""

    id = ObjProperty("id", object)

    def __init__(self, properties: _t.Optional[_t.Dict[str, _t.Any]] = None, **kwds):
        self._unique_watcher = None
        self.name2property = self.__class__.name2property
        self.properties = {}
        if properties:
            kwds.update(properties)
        for name, prop in self.name2property.items():
            prop.__set__(self, kwds.get(name))

    def __str__(self):
        return "%s({%s})" % (
            self.__class__.__name__,
            ", ".join("%r: %r" % (k, v.__get__(self, self.__class__))
                      for k, v in self.name2property.items())
        )

    def __eq__(self, __o):
        if isinstance(__o, Obj):
            return self.id == __o.id
        return self.id == __o

    def __setattr__(self, __name: str, __value):
        if __name == "id" and self._unique_watcher is not None:
            self._unique_watcher(getattr(self, __name), __value)
        super().__setattr__(__name, __value)

    @property
    def unique_watcher(self):
        if self._unique_watcher is None:
            raise AttributeError("unique_watcher has not been set")
        return self._unique_watcher

    @unique_watcher.setter
    def unique_watcher(self, value: WatcherType):
        self._unique_watcher = value

    __repr__ = __str__


ExpectObj = _t.TypeVar("ExpectObj", bound=Obj)


class Collection(_t.Generic[ExpectObj]):
    """Object collection"""

    def __init__(self, obj_type: _t.Type[ExpectObj], objs: _t.Optional[dict] = None):
        self.obj_type = obj_type
        self._objs: _t.Dict[_t.Any, ExpectObj] = objs or {}

    def __str__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__, self.obj_type.__name__, self._objs
        )

    def __len__(self):
        return self._objs.__len__()

    def __iter__(self):
        return self._objs.values().__iter__()

    def __getitem__(self, key):
        return self._objs[key]

    def __setitem__(self, key, obj: ExpectObj):
        if key != obj.id:
            raise KeyError(key)
        self._objs[key] = obj

    def __delitem__(self, key):
        del self._objs[key]

    def __contains__(self, __o):
        return __o in self._objs

    def unique_watcher(self, old, new):
        if new in self._objs:
            raise KeyError(new)
        self._objs[new] = self._objs[old]
        del self._objs[old]

    def add(self, obj: ExpectObj):
        """Add a obj. Raise `KeyError` if is exists"""
        if obj.id in self._objs:
            raise KeyError(obj.id)
        self.set(obj)

    def set(self, obj: ExpectObj):
        """Set a obj. Recover if is exists"""
        obj.unique_watcher = self.unique_watcher
        self._objs[obj.id] = obj

    def update(self, objs: _t.Iterable[ExpectObj]):
        """Update from obj list"""
        for obj in objs:
            self.set(obj)

    def create(self, **kwargs):
        """Create a obj. Raise `KeyError` if is exists"""
        self.add(self.obj_type(**kwargs))

    def get(self, id, default=None):
        """Get a obj by id"""
        return self._objs.get(id, default)

    def items(self):
        return self._objs.items()

    def keys(self):
        return self._objs.keys()

    def values(self):
        return self._objs.values()


class Collections(object):
    """Collections"""

    def __init__(self):
        self._collections: _t.Dict[_t.Type[Obj], Collection] = {}

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join("%r=%r" % (k.__name__, v)
                      for k, v in self._collections.items())
        )

    def __len__(self):
        return self._collections.__len__()

    def __iter__(self):
        return self._collections.values().__iter__()

    def __getitem__(self, key: _t.Type[ExpectObj]) -> Collection[ExpectObj]:
        return self._collections[key]

    def __setitem__(self, key: _t.Type[ExpectObj], value: Collection[ExpectObj]):
        if key != value.obj_type:
            raise KeyError
        self._collections[key] = value

    def __delitem__(self, key: _t.Type[ExpectObj]):
        del self._collections[key]

    def __contains__(self, __o):
        return __o in self._collections

    def add(self, collection: Collection[ExpectObj]):
        """Add a collection. Raise `KeyError` if is exists"""
        if collection.obj_type in self._collections:
            raise KeyError
        self.set(collection)

    def set(self, collection: Collection[ExpectObj]):
        """Set a collection. Recover if is exists"""
        self._collections[collection.obj_type] = collection

    def update(self, collections: _t.Iterable[Collection[ExpectObj]]):
        """Update from collection list"""
        for collection in collections:
            self.set(collection)

    def create(self, obj_type: _t.Type[ExpectObj]):
        """Create a collection. Raise `KeyError` if is exists"""
        self.add(Collection(obj_type))

    def get(self, obj_type: _t.Type[ExpectObj]) -> Collection[ExpectObj]:
        """Get a collection by obj_type, auto create if is not exists"""
        if obj_type not in self._collections:
            collection = Collection(obj_type)
            self.add(collection)
            return collection
        return self._collections[obj_type]

    def items(self):
        return self._collections.items()

    def keys(self):
        return self._collections.keys()

    def values(self):
        return self._collections.values()


class CollectionsIO(object):
    """Save or load collections"""

    def __init__(self, collections: Collections):
        self._file: _t.Union[_io.BufferedRandom, None] = None
        self.headers = {"encoding": "UTF-8"}
        self.collections = collections

    def open(self, file: _t.Union[str, _os.PathLike, _io.BufferedRandom]):
        if isinstance(file, _io.BufferedRandom):
            self._file = file
        else:
            dirpath = _os.path.dirname(file)
            if dirpath and not _os.path.exists(dirpath):
                _os.makedirs(dirpath)
            self._file = open(file, "rb+" if _os.path.exists(file) else "wb+")
        self.load()

    def close(self):
        if self._file is not None:
            self.save()
            self.file.close()

    def load(self):
        self.file.seek(0)
        tokeninfos = _tokenize.tokenize(self.file.readline)
        for tokeninfo in tokeninfos:
            if tokeninfo.type == _tokenize.ENCODING:
                self.headers["encoding"] = tokeninfo.string
                break
        tokeninfos.close()
        self.file.seek(0)
        for line in self.file:
            collection: Collection = eval(line, eval_globals)
            self.collections.get(collection.obj_type).update(collection)

    def save(self):
        self.file.seek(0)
        self.file.truncate()
        for collection in self.collections.values():
            self.file.write(f"{collection}\n".encode(self.headers["encoding"]))
        self.file.flush()

    @property
    def file(self):
        if self._file is None:
            raise AttributeError("File has not been open")
        return self._file


eval_builtins: _t.Dict[str, type] = {}
eval_globals: _t.Dict[str, _t.Union[type, _t.Dict[str, type]]] = {
    "__builtins__": eval_builtins,
}


def registry_type(type: type):
    """Registry a type for eval"""
    eval_globals[type.__name__] = type


def registry_builtin(type: type):
    """Registry a builtin type for eval"""
    eval_builtins[type.__name__] = type


registry_builtin(str)
registry_builtin(bytes)
registry_builtin(int)
registry_builtin(float)
registry_type(Collection)
registry_type(Obj)
