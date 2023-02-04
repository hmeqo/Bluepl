from __future__ import annotations
import os
import tokenize as _tokenize
import typing as _t

types = {
    "str": str,
    "bytes": bytes,
    "int": int,
    "float": float,
    "len": len,
}
eval_g = {"__builtins__": types}


class Record(object):
    """记录"""

    def __init__(self, table: Table, values: list, ignore_increment=False):
        """
        Args:
            table (Table): 所属表
            values (list): 记录值

        Raises:
            ValueError: 验证失败时抛出此异常
        """
        self._table = table
        self._values = values
        for i, field in enumerate(table.fields.__values__()):
            if not ignore_increment and field.autoincrement:
                # 自增
                if table.records:
                    self._values[i] = table.records[-1][i] + field.increment
                else:
                    self._values[i] = field.init_increment
        # 验证值
        if not self._table.validate_record(self):
            raise ValueError(self._values)

    def __str__(self):
        fields = self._table.fields
        return "%s(%s)" % (self.__class__.__name__, ", ".join(
            "%s=%r" % (k, v) for k, v in zip(fields, self._values)
        ))

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return self._values.__iter__()

    def __getitem__(self, key: _t.Union[int, str]):
        if isinstance(key, int):
            return self._values[key]
        for index, field_name in enumerate(self._table.fields):
            if field_name == key:
                return self._values[index]
        raise AttributeError(key)

    def __setitem__(self, key: _t.Union[int, str], value):
        # key 转换为索引
        if isinstance(key, int):
            index = key
        else:
            for index, field_name in enumerate(self._table.fields):
                if field_name == key:
                    break
            else:
                raise AttributeError(key)
        # 如果不是赋相同的值
        if self._values[index] != value:
            record = self.__copy__()
            record._values[index] = value
            if (not self._table.validate_value(key, value)
                    or not self._table.validate_constrains(record)):
                raise ValueError(value)
            self._values[index] = value

    def __setattr__(self, name: str, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self.__setitem__(name, value)

    def __copy__(self):
        obj = object.__new__(self.__class__)
        obj._table = self._table
        obj._values = self._values.copy()
        return obj

    # 以下 dunders 方法是为了避免被认为是字段名而设计的

    def __items__(self):
        return zip(self._table.fields, self._values)

    def __keys__(self):
        return self._table.fields.__keys__()

    def __values__(self):
        return self._values

    __repr__ = __str__
    __getattr__ = __getitem__


class Records(_t.List[Record]):
    """记录集合"""

    def __init__(self, table: Table):
        """
        Args:
            table (Table): 所属表
        """
        self.table = table
        super().__init__()

    def append(self, record: _t.Union[Record, list]):
        """添加记录"""
        if not isinstance(record, Record):
            record = Record(self.table, record)
        super().append(record)

    def values(self):
        return [i.__values__() for i in self]


class Field(object):
    """字段"""

    def __init__(
        self,
        type: type,
        nullable=True,
        unique=False,
        autoincrement=False,
        init_increment=1,
        increment=1,
    ):
        """
        Args:
            type (ExpectType): 字段类型
            nullable (bool, optional): 可否为空值, 如果设置了自增则此参数无效. Defaults to True.
            unique (bool, optional): 唯一性. Defaults to False.
            autoincrement (bool, optional): 自增. Defaults to False.
            init_increment (int, optional): 初始增量. Defaults to 1.
            increment (int, optional): 增量. Defaults to 1.
        """
        self.type = type
        self.nullable = nullable
        self.unique = unique
        self.autoincrement = autoincrement
        self.init_increment = init_increment
        self.increment = increment

    def __str__(self):
        return "%s(type=%s, nullable=%s, unique=%s, autoincrement=%s)" % (
            self.__class__.__name__, self.type, self.nullable, self.unique,
            self.autoincrement,
        )

    __repr__ = __str__


class Fields(object):
    """字段集合"""

    def __init__(self, **fields: Field):
        """
        Args:
            **fields (Field): 字段名和字段
        """
        self._fields = fields

    def __str__(self):
        return "%s%r" % (self.__class__.__name__, tuple(self._fields.keys()))

    def __len__(self):
        return len(self._fields)

    def __iter__(self):
        return self._fields.__iter__()

    def __getitem__(self, key: _t.Union[int, str]):
        if isinstance(key, str):
            return self._fields[key]
        values = self._fields.values().__iter__()
        while key:
            values.__next__()
            key -= 1
        return values.__next__()

    # 以下 dunders 方法是为了避免被认为是字段名而设计的

    def __items__(self):
        return self._fields.items()

    def __keys__(self):
        return self._fields.keys()

    def __values__(self):
        return self._fields.values()

    def __index__(self, name: str):
        for index, field_name in enumerate(self._fields):
            if field_name == name:
                return index
        raise ValueError(name)

    __repr__ = __str__
    __getattr__ = __getitem__


class Table(object):
    """表"""

    def __init__(self, **fields: Field):
        """
        Args:
            **fields (Field): 字段名和字段
        """
        self.fields = Fields(**fields)
        self.f = fields
        self.records = Records(self)
        self.r = self.records
        # 检查约束
        self.check_constrains: _t.List[str] = []

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self.fields)

    def validate_record(self, record: Record):
        """验证记录"""
        if all(self.validate_value(i, v) for i, v in enumerate(record)):
            # 通过值验证后检查约束
            return self.validate_constrains(record)
        return False

    def validate_constrains(self, record: Record):
        """检查约束"""
        g = eval_g.copy()
        g.update(record.__items__())
        for constrain in self.check_constrains:
            try:
                if not eval(constrain, g):
                    return False
            except Exception as e:
                print(e)
                return False
        return True

    def validate_value(self, key: _t.Union[int, str], value):
        """按照某个字段的要求验证值"""
        field = self.fields[key]
        # 判断类型和nullable
        if isinstance(value, field.type) or field.nullable and value is None:
            if field.unique:
                # 判断唯一性
                for record in self.records:
                    if record[key] == value:
                        return False
            return True
        return False

    def append(self, values: _t.Iterable, ignore_increment=False):
        """添加记录"""
        self.records.append(
            Record(self, list(values), ignore_increment=ignore_increment))

    __repr__ = __str__


class Tables(object):
    """表集合"""

    def __init__(self, **tables: Table):
        """
        Args:
            **tables (Table): 表名和表
        """
        self._tables: _t.Dict[str, Table] = tables

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self._tables)

    def __len__(self):
        return len(self._tables)

    def __iter__(self):
        return self._tables.__iter__()

    def __getitem__(self, key: str):
        return self._tables[key]

    def __setitem__(self, key: str, value: Table):
        if key in self._tables:
            raise KeyError("Is exists: %r" % key)
        self._tables[key] = value

    def __delitem__(self, key: str):
        del self._tables[key]

    def __setattr__(self, name: str, value: Table):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self.__setitem__(name, value)

    # Specify dunders

    def __items__(self):
        return self._tables.items()

    def __keys__(self):
        return self._tables.keys()

    def __values__(self):
        return self._tables.values()

    __repr__ = __str__
    __getattr__ = __getitem__
    __delattr__ = __delitem__


class PySqlDB(object):
    """数据库"""

    def __init__(self, key=None):
        self._file: _t.Union[_t.BinaryIO, None] = None
        self._key = key
        self.tables = Tables()
        self.headers = {"encoding": "UTF-8", "version": "1.0.0"}

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self.tables)

    @staticmethod
    def on_error(exc: Exception):
        print(exc)

    def open(self, file: _t.Union[str, os.PathLike, _t.BinaryIO]):
        """打开数据库文件"""
        if isinstance(file, _t.BinaryIO):
            self._file = file
        else:
            dirpath = os.path.dirname(file)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath)
            self._file = open(file, "ab+")
        self.read()

    def close(self):
        """关闭数据库文件"""
        self.write()
        self.file.close()

    def read(self):
        """从文件中同步数据"""
        self.file.seek(0)
        tokeninfos = _tokenize.tokenize(self.file.readline)
        key = ""
        headers = {}
        # 解析 header
        for tokeninfo in tokeninfos:
            if tokeninfo.type == _tokenize.NEWLINE:
                break
            try:
                if tokeninfo.type == _tokenize.ENCODING:
                    headers["encoding"] = tokeninfo.string
                elif tokeninfo.type == _tokenize.NAME:
                    key = tokeninfo.string
                elif key == "version" and tokeninfo.type != _tokenize.OP:
                    headers[key] = eval(tokeninfo.string, eval_g)
                    key = ""
            except Exception as e:
                self.on_error(e)
                key = ""
        self.headers.update(headers)
        table_name = self.file.readline().decode().strip()
        while table_name:
            # 解析表
            table = Table()
            self.tables[table_name] = table
            fields = {}
            # 解析字段
            for i in self.file.readline().decode().split(":"):
                try:
                    field = [eval(j, eval_g) for j in i.split(",")]
                except Exception as e:
                    self.on_error(e)
                else:
                    fields[field[0]] = Field(
                        field[1],
                        nullable=field[2],
                        unique=field[3],
                        autoincrement=field[4],
                        init_increment=field[5],
                        increment=field[6],
                    )
            table.fields = Fields(**fields)
            # 解析约束
            try:
                constrains = list(eval(self.file.readline().decode(), eval_g))
            except Exception as e:
                constrains = []
                self.on_error(e)
            table.check_constrains = constrains
            # 解析记录
            try:
                for i in eval(self.file.readline().decode(), eval_g):
                    table.append(i, ignore_increment=True)
            except Exception as e:
                self.on_error(e)
            table_name = self.file.readline().decode().strip()

    def write(self):
        """更新并写入数据库文件"""
        self.file.seek(0)
        self.file.truncate()
        self.file.write(f"version='{self.headers['version']}'\n".encode())
        for table_name, table in self.tables.__items__():
            # 写入表名
            self.file.write(table_name.encode() + b"\n")
            # 写入字段
            fields = []
            for field_name, field in table.fields.__items__():
                fields.append(",".join(map(str, (
                    repr(field_name), field.type.__name__, field.nullable,
                    field.unique, field.autoincrement, field.init_increment,
                    field.increment,
                ))).encode())
            self.file.write(b":".join(fields) + b"\n")
            # 写入约束
            self.file.write(str(table.check_constrains).encode() + b"\n")
            # 写入记录
            self.file.write(str(table.records.values()).encode() + b"\n")

    def sql(self, sql: str):
        """使用sql语句"""
        # TODO 实现通过 sql 语句执行操作

    @property
    def file(self):
        if self._file:
            return self._file
        raise AttributeError

    __repr__ = __str__


def main():
    db = PySqlDB()
    db.on_error = lambda exc: print(exc)
    # db.open("test.db")
    db.tables.test = Table(
        id=Field(int, unique=True, autoincrement=True),
        name=Field(str, nullable=False),
    )
    db.tables.test.append([None, "张三"])
    print(db)
    print(db.tables.test.records)
    # db.close()


if __name__ == "__main__":
    main()
