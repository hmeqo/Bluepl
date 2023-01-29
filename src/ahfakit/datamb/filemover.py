import os
import shutil


class FileMover(object):

    def __init__(self):
        self.files = []

    def add_file(self, filename: str, is_file: bool):
        self.files.append((filename, is_file))

    def move(self, path: str, despath: str):
        if os.path.isfile(despath):
            return False
        if os.path.isdir(path):
            files = self.files.copy()
            try:
                file_list = os.scandir(path)
            except Exception as exc:
                print("Error:", exc)
                return False
            if not os.path.exists(despath):
                os.makedirs(despath)
            for i in file_list:
                try:
                    index = files.index((i.name, i.is_dir()))
                    shutil.move(i.path, os.path.join(despath, i.name))
                except IndexError:
                    pass
                except Exception as exc:
                    print("Error:", exc)
                else:
                    del files[index]
            if files:
                return False
            else:
                os.remove(path)
        return True
