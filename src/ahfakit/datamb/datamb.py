import json
import os
import configparser
import abc as _abc

from .node import *


class IO(object):

    def __init__(self, tree: Node, filepath: str, mode="a+", encoding="UTF-8"):
        self.tree = tree
        self.filepath = os.path.realpath(filepath)
        self.encoding = encoding
        self.filedir = os.path.dirname(self.filepath)
        if not os.path.exists(self.filedir):
            os.makedirs(self.filedir)
        self.file = open(filepath, mode, encoding=encoding)

    @_abc.abstractmethod
    def save(self):
        """保存"""
        raise NotImplementedError

    @_abc.abstractmethod
    def load(self):
        """读取"""
        raise NotImplementedError

    def close(self):
        self.file.close()


class Json(IO):

    indent = 4

    def save(self):
        data = self.tree.jsonify()
        self.file.seek(0)
        self.file.truncate()
        json.dump(data, self.file, ensure_ascii=False, indent=self.indent)
        self.file.flush()

    def load(self):
        self.file.seek(0)
        data = json.load(self.file)
        self.tree.value = data


class Ini(IO):

    def __init__(self, tree: MapTree, filepath: str, mode="a+", encoding="UTF-8"):
        if not isinstance(tree, MapTree):
            raise TypeError()
        for i in tree.values():
            if not isinstance(i, MapTree):
                raise ValueError()
            for j in i.values():
                if isinstance(j, Tree):
                    raise ValueError()
        super().__init__(tree, filepath, mode, encoding)

    def save(self):
        config = configparser.ConfigParser()
        data = self.tree.dump_pkg()
        for section in data:
            config.add_section(section)
            for key, value in data[section].items():
                config.set(section, key, value)
        self.file.seek(0)
        self.file.truncate()
        config.write(self.file)

    def load(self):
        config = configparser.ConfigParser()
        self.file.seek(0)
        config.read_file(self.file)
        self.tree.load_pkg({
            section: dict(config.items(section))
            for section in config.sections()})
