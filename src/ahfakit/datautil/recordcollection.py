"""
Usage:

```
class MyRecord(Record):

    # name is "id", type is int, autoincrement
    id = AutoincProperty("id")
    # name is "name", type is str, nullable
    name = RecordProperty("name", (str, NONE_TYPE))
    # name is "age", type is int, default to 0
    age = RecordProperty("age", int, default=0)

collections = Collections()
myobjs = collections.get(MyRecord)
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

AnyObj = _t.TypeVar("AnyObj")
WatcherType = _t.Callable[[_t.Any, _t.Any], None]

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


class MissingError(Exception):
    pass


def ref(value: AnyObj) -> _t.Callable[[], AnyObj]:
    """return the value when the inner function invoked,
    return inner function.
    """
    return lambda: value


class RecordProperty(_t.Generic[AnyObj]):
    """A property"""

    def __init__(
        self,
        name: str,
        type: _t.Union[_t.Type[AnyObj], _t.Tuple[_t.Type[AnyObj], ...]],
        default: _t.Union[AnyObj, _t.Callable[[], AnyObj], None] = None,
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

    @_t.overload
    def __get__(self, instance: None, obj_type: _t.Type[Record]) -> RecordProperty:
        ...

    @_t.overload
    def __get__(self, instance: Record, obj_type: _t.Type[Record]) -> AnyObj:
        ...

    def __get__(
        self,
        instance: _t.Optional[Record],
        obj_type: _t.Type[Record],
    ) -> _t.Union[AnyObj, RecordProperty]:
        if instance is None:
            return self
        return instance.properties[self.name]

    def __set__(self, instance: Record, value: _t.Optional[AnyObj]):
        if value is None:
            # 判断有没有默认值
            if self.default is not None:
                if callable(self.default):
                    value = self.default()
                else:
                    value = self.default
            # 判断是否不允许为空
            elif not self.nullable:
                raise MissingError(self.name)
        if not isinstance(value, self.type):
            raise TypeError(value)
        if not all(i(value) for i in self.validators):
            raise ValueError(value)
        instance.properties[self.name] = value


class AutoincProperty(RecordProperty[int]):
    """Autoincrement Property"""

    def __init__(self, name: str, init=1, increment=1):
        super().__init__(name, int)
        self.init = init
        self.increment = increment
        self.current = init - 1

    def __set__(self, instance: Record, value: _t.Optional[int]):
        if isinstance(value, int):
            self.current = value
            super().__set__(instance, value)
        else:
            super().__set__(instance, self._next())

    def _next(self):
        self.current += 1
        return self.current


class Record(object):

    id = RecordProperty("id", object)

    def __init__(
        self,
        items: _t.Optional[_t.Dict[str, _t.Any]] = None,
        **kwds: _t.Any,
    ):
        self._unique_watcher: _t.Union[WatcherType, None] = None
        self.properties: _t.Dict[str, _t.Any] = {}
        if items:
            kwds.update(items)
        for prop in {
            i.name: i
            for i in {
                name: prop
                for class_ in reversed(self.__class__.mro())
                for name, prop in class_.__dict__.items()
                if isinstance(prop, RecordProperty)
            }.values()
        }.values():
            prop.__set__(self, kwds.pop(prop.name, None))
        if kwds:
            raise KeyError(tuple(kwds))

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__, self.properties
        )

    def __eq__(self, __o):
        if isinstance(__o, Record):
            return self.id == __o.id
        return self.id == __o

    def __setattr__(self, __name: str, __value):
        if (
            getattr(self.__class__, __name, None) is self.__class__.id
            and self._unique_watcher is not None
        ):
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


ObjType = _t.TypeVar("ObjType", bound=Record)


class RecordCollection(_t.Generic[ObjType]):
    """Object collection"""

    def __init__(
        self,
        obj_type: _t.Type[ObjType],
        objs: _t.Optional[dict] = None,
    ):
        self.obj_type = obj_type
        self._objs: _t.Dict[_t.Any, ObjType] = objs or {}

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

    def __setitem__(self, key, obj: ObjType):
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

    def add(self, obj: ObjType):
        """Add a obj. Raise `KeyError` if is exists"""
        if obj.id in self._objs:
            raise KeyError(obj.id)
        self.set(obj)

    def set(self, obj: ObjType):
        """Set a obj. Recover if is exists"""
        obj.unique_watcher = self.unique_watcher
        self._objs[obj.id] = obj

    def update(self, objs: _t.Iterable[ObjType]):
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


class RecordCollections(object):
    """Collections"""

    def __init__(self):
        self._collections: _t.Dict[_t.Type[Record], RecordCollection] = {}

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

    def __getitem__(self, key: _t.Type[ObjType]) -> RecordCollection[ObjType]:
        return self._collections[key]

    def __setitem__(self, key: _t.Type[ObjType], value: RecordCollection[ObjType]):
        if key != value.obj_type:
            raise KeyError
        self._collections[key] = value

    def __delitem__(self, key: _t.Type[ObjType]):
        del self._collections[key]

    def __contains__(self, __o):
        return __o in self._collections

    def add(self, collection: RecordCollection[ObjType]):
        """Add a collection. Raise `KeyError` if is exists"""
        if collection.obj_type in self._collections:
            raise KeyError
        self.set(collection)

    def set(self, collection: RecordCollection[ObjType]):
        """Set a collection. Recover if is exists"""
        self._collections[collection.obj_type] = collection

    def update(self, collections: _t.Iterable[RecordCollection[ObjType]]):
        """Update from collection list"""
        for collection in collections:
            self.set(collection)

    def create(self, obj_type: _t.Type[ObjType]):
        """Create a collection. Raise `KeyError` if is exists"""
        self.add(RecordCollection(obj_type))

    def get(self, obj_type: _t.Type[ObjType]) -> RecordCollection[ObjType]:
        """Get a collection by obj_type, auto create if is not exists"""
        if obj_type not in self._collections:
            collection = RecordCollection(obj_type)
            self.add(collection)
            return collection
        return self._collections[obj_type]

    def items(self):
        return self._collections.items()

    def keys(self):
        return self._collections.keys()

    def values(self):
        return self._collections.values()


class RecordCollectionsIO(RecordCollections):
    """Save and load feature for collections"""

    def __init__(self):
        super().__init__()
        self._file: _t.Union[_io.BufferedRandom, None] = None
        self.encoding = "utf-8"

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
        self.encoding = tokeninfos.send(None).string
        tokeninfos.close()
        self.file.seek(0)
        for line in self.file:
            collection: RecordCollection = eval(line, eval_globals)
            self.get(collection.obj_type).update(collection)

    def save(self):
        self.file.seek(0)
        self.file.truncate()
        for collection in self.values():
            self.file.write(f"{collection}\n".encode(self.encoding))
        self.file.flush()

    @property
    def file(self):
        if self._file is None:
            raise AttributeError("File has not been open")
        return self._file


registry_builtin(str)
registry_builtin(bytes)
registry_builtin(int)
registry_builtin(float)
registry_type(RecordCollection)
registry_type(Record)
