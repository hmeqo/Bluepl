"""版本信息"""

from typing import Sequence


class VersionInfo(object):

    def __init__(
        self,
        major: int,
        minor: int,
        micro: int,
        releaselevel: str,
        serial=0,
        date: Sequence[int] = (0, 0, 0)
    ):
        self.major = major
        self.minor = minor
        self.micro = micro
        self.releaselevel = releaselevel
        self.serial = serial
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]

        self.version = "%s.%s.%s" % (major, minor, micro)
        self.release = "%s.%s" % (self.releaselevel, self.serial)
        self.date = "/".join(map(str, date))
        self.full_version = self.version + "." + self.release

    def __str__(self):
        return self.full_version


def main():
    version_info = VersionInfo(1, 1, 1, "Final", date=(2022, 3, 25))
    print(version_info.full_version)
    print(version_info.date)


if __name__ == "__main__":
    main()
