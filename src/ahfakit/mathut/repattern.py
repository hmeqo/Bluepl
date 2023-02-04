import re as _re


class Re(object):
    """匹配数字."""

    # 符号
    signed = r"[\\+-]?"
    # 无符号整数
    unsigned_int = r"\d+"
    # 整数
    integer = signed + unsigned_int
    # 无符号小数
    unsigned_dec = unsigned_int + r"(\.\d+)"
    # 小数
    decimals = signed + unsigned_dec
    # 无符号数
    unsigned_num = unsigned_dec + r"?"
    # 数
    number = signed + unsigned_num
    # 零
    zero = signed + r"0+(\.0+)?"

    # 编译上面的正则
    signed = _re.compile(signed)
    unsigned_int = _re.compile(unsigned_int)
    integer = _re.compile(integer)
    unsigned_dec = _re.compile(unsigned_dec)
    decimals = _re.compile(decimals)
    unsigned_num = _re.compile(unsigned_num)
    number = _re.compile(number)
    zero = _re.compile(zero)

    # 方法会用到的pattern
    _is_int = _re.compile(r"^" + integer.pattern + r"$")
    _is_float = _re.compile(r"^" + decimals.pattern + r"$")
    _is_num = _re.compile(r"^" + number.pattern + r"$")
    _is_zero = _re.compile(r"^" + zero.pattern + r"$")

    @classmethod
    def is_int(cls, s):
        """是否是整数串."""
        return bool(cls._is_int.match(s))

    @classmethod
    def is_float(cls, s):
        """是否是小数串."""
        return bool(cls._is_float.match(s))

    @classmethod
    def is_num(cls, s):
        """是否是数字串."""
        return bool(cls._is_num.match(s))

    @classmethod
    def is_zero(cls, s):
        """是否为0."""
        return bool(cls._is_zero.match(s))
