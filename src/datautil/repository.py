import marshal as _marshal


class PyRepository(object):

    base_imports = {"import io"}

    def __init__(self, fp):
        self.encoding = "UTF-8"
        self.fp = fp
        self.imports = set()
        self.data = {}

    def has(self, name):
        return name in self.data

    def set(self, name, value):
        if type(name) is not str or type(value) is not str:
            raise TypeError(
                "Type must be str."
            )
        self.data[name] = value

    def set_marshal(self, name, value):
        self.set(name, repr(_marshal.dumps(value)))

    def set_bytes(self, name, fp):
        with open(fp, "br") as file:
            self.set(name, file.read())

    def set_bytesio(self, name, fp):
        with open(fp, "br") as file:
            self.set(name, "io.BytesIO(%r)" % file.read())

    def set_stringio(self, name, fp):
        with open(fp, "r") as file:
            self.set(name, "io.StringIO(%r)" % file.read())

    def load(self):
        with open(self.fp, "r", encoding=self.encoding) as file:
            self.imports.clear()
            self.data.clear()
            for line in file:
                nv = line.split(" = ")
                if len(nv) == 2:
                    self.data[nv[0]] = nv[1].rstrip()
                else:
                    self.imports.add("import io")

    def save(self):
        self.imports.update(self.base_imports)
        with open(self.fp, "w", encoding=self.encoding) as file:
            for i in self.imports:
                file.write(i + "\n")
            for k, v in self.data.items():
                file.write(k + " = " + v + "\n")


def main():
    repository = PyRepository("test.py")
    repository.set("name", "123")
    print(repository.imports)
    print(repository.data)


if __name__ == "__main__":
    main()
