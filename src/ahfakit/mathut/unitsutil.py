from typing import Optional as _Optional

BYTE_UNITS = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB")
BPS_UNITS = ("bps", "Kbps", "Mbps", "Gbps", "Tbps",
             "Pbps", "Ebps", "Zbps", "Ybps", "Bbps")
BYTE_SYSTEM = 1024
BPS_SYSTEM = 1000

KB = BYTE_SYSTEM
MB = KB * BYTE_SYSTEM
GB = MB * BYTE_SYSTEM
TB = GB * BYTE_SYSTEM
PB = TB * BYTE_SYSTEM
EB = PB * BYTE_SYSTEM
ZB = EB * BYTE_SYSTEM
YB = ZB * BYTE_SYSTEM
BB = YB * BYTE_SYSTEM


def convert(units_list, system, num, dp=None, units="", sep=""):
    """单位与数值转换.

    Arguments:
        units_list: 单位列表
        system: 进制
        obj: 要转换的对象
        dp: 数字转换单位时的小数精度
        units: 指定单位
        sep: 数字和单位之间的分割符号
    """
    if units and units not in units_list:
        return ""
    elif isinstance(num, (int, float)):
        index = 0
        if units:
            index = units_list.index(units)
            num /= system ** index
        else:
            while num >= system and index < len(units_list) - 1:
                num /= system
                index += 1
        if dp is not None:
            num = round(num, dp if dp else None)
        num = str(num) + sep + units_list[index]
    elif isinstance(num, str):
        for i in range(len(units_list) - 1, -1, -1):
            if num.endswith(units_list[i]):
                num = float(num[:-len(units_list[i])].rstrip(sep))
                for _ in range(i):
                    num *= system
                break
        num = int(num)
    return num


def cvt_bytes(num, dp: _Optional[int] = None, units="", sep=""):
    """字节单位数字相互转换."""
    units = units.upper()
    if isinstance(num, str):
        num = num.upper()
    return convert(BYTE_UNITS, BYTE_SYSTEM, num, dp, units, sep)


def cvt_bps(num, dp: _Optional[int] = None, units="", sep=""):
    """bps单位数字相互转换."""
    units = units.title()
    if isinstance(num, str):
        num = num.title()
    return convert(BPS_UNITS, BPS_SYSTEM, num, dp, units, sep)
