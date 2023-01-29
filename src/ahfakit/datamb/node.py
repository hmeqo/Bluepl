from __future__ import annotations
import copy
import typing as _t
import marshal as _marshal

from .validators import ExpectValidator, ExpectValidators


def _exc_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception:
            return None
        return result
    return wrapper


class _MetaNode(type):

    def __init__(cls, name, bases, attr):
        super().__init__(name)
        if "load_pkg" in attr:
            cls.load_pkg = _exc_catcher(attr["load_pkg"])


class Node(metaclass=_MetaNode):
    """节点基类"""

    get_type = type

    ExpectType = _t.Union[type, _t.Tuple[type, ...]]

    def __init__(
        self,
        value,
        type: _t.Optional[ExpectType] = None,
        validator: _t.Optional[ExpectValidators] = None
    ):
        self.validators: _t.List[ExpectValidator] = []
        if validator is not None:
            if isinstance(validator, _t.Iterable):
                self.validators.extend(validator)
            else:
                self.validators.append(validator)
        self._type = self.get_type(value) if type is None else type
        if not isinstance(value, self._type):
            raise TypeError("Incorrect type of %r: %s" % (
                value, self._type))
        elif not self.validate(value):
            raise ValueError("Validate failed: %r" % value)
        self._value = self.parse(value)
        self._default = copy.deepcopy(value)

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self._value)

    def __len__(self):
        return len(self._value)

    def __getitem__(self, key: _t.Union[str, int]) -> Node:
        raise NotImplementedError

    def __setitem__(self, key: _t.Union[str, int], value):
        raise NotImplementedError

    def __delitem__(self, key: _t.Union[str, int]):
        raise NotImplementedError

    def __contains__(self, other):
        return other in self._value

    def __eq__(self, other):
        if isinstance(other, Node):
            return self._value == other._value
        return self._value == other

    @staticmethod
    def parse(obj):
        """解析为此类型的合法值"""
        return obj

    @staticmethod
    def items_of(iterable) -> _t.Iterable:
        """按照此类型返回键值对"""
        raise NotImplementedError

    def _assignment(self, value):
        """此类型对于值的赋值方式"""
        self._value = value

    def jsonify(self):
        """返回 json 格式数据"""
        return self.value

    def load_pkg(self, s):
        """解析并载入"""
        self.value = s

    def dump_pkg(self):
        """打包"""
        return self.value

    def restore(self):
        """恢复默认"""
        self._value = copy.deepcopy(self.default)

    def validate(self, value):
        """检查值是否合法"""
        return isinstance(value, self._type) and all(f(value) for f in self.validators)

    def validate_key(self, key) -> bool:
        """检查键是否合法"""
        raise NotImplementedError

    def items(self) -> _t.Iterable[_t.Tuple[_t.Any, Node]]:
        """获取键值对"""
        raise NotImplementedError

    def keys(self) -> _t.Iterable[_t.Any]:
        """获取键"""
        raise NotImplementedError

    def values(self) -> _t.Iterable[Node]:
        """获取值"""
        raise NotImplementedError

    def insert(self, key: int, node: Node):
        """插入元素"""
        raise NotImplementedError

    def set(self, key: str, node: Node):
        """设置元素"""
        raise NotImplementedError

    def remove(self, value: _t.Any):
        """按照值移除元素"""
        raise NotImplementedError

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, Node):
            value = value.value
        if self.validate(value):
            self._assignment(value)

    @property
    def default(self):
        return self._default

    @property
    def type(self):
        return self._type

    __repr__ = __str__


class ArgTree(Node):
    """Base of ArgTree, the key and value type is immutable."""

    def __str__(self):
        return "%s({%s\n})" % (
            self.__class__.__name__,
            "".join("\n  %s=%r," % (k, v) for k, v in self.items())
        )

    def __getitem__(self, key) -> Node:
        return self._value[key]

    def __setitem__(self, key, value):
        if self.validate_key(key):
            self._value[key].value = value

    def __delitem__(self, key):
        if self.validate_key(key):
            del self._value[key]

    def _assignment(self, value):
        for k, v in self.items_of(value):
            self[k] = v

    def load_pkg(self, obj):
        for k, v in self.items_of(obj):
            if self.validate_key(k):
                self[k].load_pkg(v)

    def dump_pkg(self):
        return repr(self.value)

    def items(self) -> _t.Iterable[_t.Tuple[_t.Any, Node]]:
        return self.items_of(self._value)

    def keys(self) -> _t.Iterable[_t.Any]:
        return (i[0] for i in self.items_of(self._value))

    def values(self) -> _t.Iterable[Node]:
        return (i[1] for i in self.items_of(self._value))


class Tree(ArgTree):
    """Base of Tree, the key and value type is mutable."""

    def _assignment(self, value):
        self._value = self.parse(value)

    def remove(self, value):
        for k, v in self.items():
            if v.value == value:
                del self[k]
                break


class PackNode(Node):
    """Pack node."""

    def load_pkg(self, s):
        self.value = _marshal.loads(bytes.fromhex(s))

    def dump_pkg(self):
        return _marshal.dumps(self.value).hex()


class StrNode(Node):
    """String node."""

    def __init__(self, value: str = "", type=str, validator=None):
        super().__init__(value, type, validator)


class IntNode(Node):
    """Integer node."""

    def __init__(self, value: int = 0, type=int, validator=None):
        super().__init__(value, type, validator)

    def load_pkg(self, s: str):
        self.value = int(s)

    def dump_pkg(self):
        return str(self.value)


class FloatNode(Node):
    """Float node."""

    def __init__(self, value: _t.Union[int, float] = 0, type=(int, float), validator=None):
        super().__init__(value, type, validator)

    def load_pkg(self, s: str):
        self.value = float(s)

    def dump_pkg(self):
        return str(self.value)


class BoolNode(Node):
    """Bool node."""

    def __init__(self, value: bool = True, type=bool, validator=None):
        super().__init__(value, type, validator)

    def load_pkg(self, s: str):
        if s == "true":
            self.value = True
        elif s == "false":
            self.value = False
        raise ValueError("The value must be bool.")

    def dump_pkg(self):
        return "true" if self.value else "false"


class ArgMapTree(ArgTree):
    """Arguments map tree."""

    _value: _t.Dict[str, Node]

    def __init__(self, value: _t.Dict[str, _t.Any] = ..., type=dict, validator=None):
        super().__init__({} if value is ... else value, type, validator)

    @staticmethod
    def parse(obj: dict):
        return {k: converter.to_node(v) for k, v in obj.items()}

    @staticmethod
    def items_of(iterable: dict):
        return iterable.items()

    def validate_key(self, key):
        return isinstance(key, str) and key in self

    def jsonify(self):
        return {k: v.jsonify() for k, v in self._value.items()}

    def dump_pkg(self):
        return {k: v.dump_pkg() for k, v in self._value.items()}


class ArgListTree(ArgTree):
    """Arguments list tree."""

    _value: _t.List[Node]

    def __init__(self, value: _t.List = ..., type=list, validator=None):
        super().__init__([] if value is ... else value, type, validator)

    @staticmethod
    def parse(obj: list):
        return [converter.to_node(i) for i in obj]

    @staticmethod
    def items_of(iterable: list):
        return enumerate(iterable)

    def validate_key(self, key):
        if not isinstance(key, int):
            return False
        return len(self) - key >= 0 if key < 0 else key < len(self)

    def jsonify(self):
        return [i.jsonify() for i in self._value]

    def dump_pkg(self):
        return [i.dump_pkg() for i in self._value]


class MapTree(Tree, ArgMapTree):
    """Map tree."""

    def set(self, key: str, node):
        if not isinstance(key, str):
            raise KeyError
        self._value[key] = converter.to_node(node)


class ListTree(Tree, ArgListTree):
    """List tree."""

    def insert(self, key: int, node):
        if not isinstance(key, int):
            raise KeyError
        self._value.insert(key, converter.to_node(node))


class Converter(object):
    """Converter for object and `Node`."""

    def __init__(self):
        self.parse_dict = {
            bool: BoolNode,
            int: IntNode,
            float: FloatNode,
            str: StrNode,
            dict: MapTree,
            list: ListTree,
        }

    def to_node(self, obj) -> Node:
        """object to `Node`."""
        if isinstance(obj, Node):
            return obj
        for k, v in self.parse_dict.items():
            if isinstance(obj, k):
                return v(obj)
        return PackNode(obj)


converter = Converter()
