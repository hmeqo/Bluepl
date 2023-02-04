from __future__ import annotations

__all__ = [
    # Major class
    "StrDecs", "Decimal",

    # Check
    "intable", "floatable", "is_num",

    # Convert
    "convert_sn", "int2str", "str2int",
]

import sys as _sys
import fractions as _fractions
from typing import Optional as _Optional

from .funcs import *


def intable(s: str):
    if s[0] in "-+":
        return s[1:].isdecimal()
    return s.isdecimal()


def floatable(s: str):
    if s[0] in "-+":
        s = s[1:]
    index = s.find(".")
    if index in (-1, 0, len(s) - 1):
        return False
    s = s[:index] + s[index+1:]
    return s.isdecimal()


def is_num(s: str):
    return intable(s) or floatable(s)


def convert_sn(str_num: str):
    """Convert scientific notation.
    把科学计数法格式的数字串转换成正常格式的数字串.
    """
    import re
    a = re.search(r"[eE]", str_num)
    if a:
        a = a.start()
        str_num_list = [str_num[:a], int(str_num[a+1:])]
        dp = StrDecs(str_num_list[0])
        if str_num_list[1] < 0:
            a = abs(str_num_list[1])
            str_num = dp.floats2ints(str_num_list[0])
            dp.dp += a
            str_num = dp.ints2floats(str_num)
        else:
            a = abs(str_num_list[1]) - dp.dp
            str_num = dp.floats2ints(str_num_list[0])
            if a > 0:
                str_num += '0' * a
                dp.dp = 0
            elif a < 0:
                dp.dp = abs(a)
                str_num = dp.ints2floats(str_num)
    return str_num


if hasattr(_sys, "get_int_max_str_digits"):
    def str2int(obj) -> int:
        if isinstance(obj, str):
            result = 0
            for char in obj:
                result = (result * 10) + ord(char) - 48
            return result
        return int(obj)

    def int2str(__n: int) -> str:
        result = []
        while __n:
            __n, a = divmod(__n, 10)
            result.append(str(a))
        return "".join(reversed(result))
else:
    str2int = int
    int2str = str


class StrDecs(object):

    def __init__(self, *ss):
        self.dp = self.get_max_dp(*ss) if ss else 0

    @classmethod
    def get_max_dp(cls, *ss):
        """迭代对象中的字符数字串的最大小数位数"""
        return max(map(cls.get_dp, ss))

    @staticmethod
    def get_dp(s: str):
        """一个字符数字串的最大小数位数"""
        index = s.find('.')
        return 0 if index == -1 else len(s) - 1 - index

    @staticmethod
    def rstrip_zero(s: str):
        """清除末尾多余的零"""
        s = s.rstrip("0")
        return s + "0" if s.endswith(".") else s

    def reserve_dp(self, s: str, dp: int):
        """保留小数, 对传入的字符串数值操作"""
        p = len(s) - self.dp + dp
        s = s.ljust(p, "0")[:p]
        return s[:-1] if s.endswith(".") else s

    def floats2ints(self, s: str):
        """小数字符串转换成整数字符串, 小数部分长度至少大于等于 `self.dp`"""
        if self.dp:
            a = s.find('.')
            if a == -1:
                return s.ljust(len(s) + self.dp, '0')
            else:
                return s.ljust(self.dp + a + 1, '0').replace('.', '', 1)
        return s

    def ints2floats(self, s: str):
        """整数字符串转换回小数字符串."""
        if self.dp:
            s = s.zfill(self.dp + (2 if s[0] in "-+" else 1))
            sl = (s[:-self.dp], s[-self.dp:])
            if int(sl[1]):
                return '.'.join(sl)
            return sl[0]
        return s


class Decimal(object):

    display_precision: _Optional[int] = None

    def __init__(self, int_n=0, decimal_place=0, precision=16):
        for i in (int_n, decimal_place, precision):
            if type(i) is not int:
                raise TypeError(
                    "Type must be %s: %r" % (int.__name__, i)
                )
        for i in (decimal_place, precision):
            if i < 0:
                raise ValueError(
                    "Can not less than 0: %r" % i
                )
        # 当前小数位数
        self.dp = decimal_place
        # 数值
        self.n = int_n
        # 1
        self.one = 10 ** self.dp
        if precision:
            self.magnify_precision(precision)

    def __repr__(self):
        # 保留 n 位数字
        n = 16
        ss = self.__str__()[:n+3]
        sign = "" if ss[0].isdecimal() else ss[0]
        # 数字和小数点
        d = ss[1:] if sign else ss
        # 数字个数大于 n
        if len(d.replace(".", "", 1)) > n:
            if "." in d:
                d = d[:n+1]
                # 如果小数点在末尾，省去小数点
                if d[-1] == ".":
                    d = d[:n]
            else:
                d = d[:n]
            d += "..."
        return "{}('{}{}')".format(self.__class__.__name__, sign, d)
        # return "{}('{}')".format(self.__class__.__name__, self.__str__())

    def __str__(self):
        integer, decimals = self.separate()
        if self.display_precision is not None:
            decimals = decimals[:self.display_precision]
        if self.n < 0:
            integer = "-" + integer
        if any(i != "0" for i in decimals):
            return ".".join([integer, decimals])
        return integer

    def __int__(self):
        return self.n // self.one

    def __float__(self):
        # result = float(".".join(self.separate()))
        # return -result if self._n < 0 else result
        return self.n / self.one

    def __complex__(self):
        return complex(str(self))

    def __bool__(self):
        return bool(self.n)

    def __abs__(self):
        new = self.copy()
        new.n = abs(new.n)
        return new

    def __pos__(self):
        return self.copy()

    def __neg__(self):
        new = self.copy()
        new.n = -new.n
        return new

    def __round__(self, n=None):
        return round(float(self), n)

    def __divmod__(self, other):
        div = self // other
        return div, self - div*other

    def __add__(self, other):
        if isinstance(other, self.__class__):
            new = self
            if new.dp < other.dp:
                new, other = other, new
            new = new.copy()
            new.n += new.magnify_int(other.n, new.dp - other.dp)
            return new
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n += new.one * other
            return new
        elif other_type is float:
            return self + self.convert_float(other)
        raise TypeError()

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            new = self.merge(other)
            new.n -= new.magnify_int(other.n, new.dp - other.dp)
            return new
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n -= new.one * other
            return new
        elif other_type is float:
            return self - self.convert_float(other)
        raise TypeError()

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            new = self
            if new.dp < other.dp:
                new, other = other, new
            new = new.copy()
            new.n = new.n * other.n // other.one
            return new
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n *= other
            return new
        elif other_type is float:
            # 乘法特殊，不需要小数位数相同
            # 所以此处使用 self.from_float 而不是 self.convert_float
            other = self.from_float(other)
            # 保证小数位数不受浮点数影响
            other.reduce_precision(self.dp)
            return self * other
        raise TypeError()

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            new = self.merge(other)
            new.n *= new.one
            new.n //= new.magnify_int(other.n, new.dp - other.dp)
            return new
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n //= other
            return new
        elif other_type is float:
            return self / self.convert_float(other)
        raise TypeError()

    def __floordiv__(self, other):
        if isinstance(other, self.__class__):
            new = self.merge(other)
            new.n //= new.magnify_int(other.n, new.dp - other.dp)
            new.one = 1
            new.dp = 0
            return new
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n = new.n // new.one // other
            new.one = 1
            new.dp = 0
            return new
        elif other_type is float:
            return self // self.convert_float(other)
        raise TypeError()

    def __mod__(self, other):
        return self - (self // other)*other

    def __pow__(self, power, modulus=None):
        if isinstance(power, self.__class__):
            new = self.merge(power)
            if power != 0:
                # 分离指数的整数和小数部分
                p_int, p_dec = power.separate()
                p_int = -int(p_int) if power < 0 else int(p_int)
                # 将小数部分转换成分数，用于开方
                p_dec = "-0." + p_dec if p_int < 0 else "0." + p_dec
                p_dec = _fractions.Fraction(p_dec)
                # 如果底数是负数，指数是小数
                if new < 0 and p_dec:
                    return complex(new) ** complex(p_dec)
                n = new.copy()
                # 计算整数部分
                if p_int:
                    n **= p_int
                # 计算小数部分
                if p_dec:
                    dms = new.root(p_dec.denominator) ** p_dec.numerator
                    # 整数部分不为 0
                    if p_int:
                        n *= dms
                    # 整数部分为 0 时，只保留小数部分计算结果
                    else:
                        n = dms
                new = n
            # power 为 0
            else:
                new.n = new.one
            return new if modulus is None else new % modulus
        power_type = type(power)
        if power_type is int or power_type is bool:
            new = self.copy()
            if power != 0:
                # 指数为负数，求底数的倒数，将指数转换成正数
                if power < 0:
                    new = 1 / new
                    power = abs(power)
                if power > 1:
                    new.n = new.n ** power // new.one ** (power - 1)
            else:
                new.n = new.one
            return new if modulus is None else new % modulus
        elif power_type is float:
            return self ** self.from_float(power)
        raise TypeError()

    def __radd__(self, other):
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n = new.one * other + new.n
            return new
        elif other_type is float:
            return self.convert_float(other) + self
        raise TypeError()

    def __rsub__(self, other):
        other_type = type(other)
        if other_type is int or other_type is float:
            new = self.copy()
            new.n = new.one * other - new.n
            return new
        elif other_type is float:
            return self.convert_float(other) - self
        raise TypeError()

    def __rmul__(self, other):
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n = other * new.n
            return new
        elif other_type is float:
            other = self.from_float(other)
            other.reduce_precision(self.dp)
            return self * other
        raise TypeError()

    def __rtruediv__(self, other):
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n = new.one ** 2 * other // new.n
            return new
        elif other_type is float:
            return self.convert_float(other) / self
        raise TypeError()

    def __rfloordiv__(self, other):
        other_type = type(other)
        if other_type is int or other_type is bool:
            new = self.copy()
            new.n = new.one * other // new.n
            new.one = 1
            new.dp = 0
            return new
        elif other_type is float:
            return self.convert_float(other) // self
        raise TypeError()

    def __rmod__(self, other):
        return other - (other // self)*self

    def __rpow__(self, other):
        other_type = type(other)
        if other_type is int or other_type is bool:
            return self.convert_int(other) ** self
        elif other_type is float:
            return self.convert_float(other) ** self
        raise TypeError()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.merge(other).n == other.merge(self).n
        other_type = type(other)
        if other_type is int or other_type is bool:
            return self.n == self.one * other
        elif other_type is float:
            return self.n == self.convert_float(other).n
        return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.merge(other).n >= other.merge(self).n
        other_type = type(other)
        if other_type is int or other_type is bool:
            return self.n >= self.one * other
        elif other_type is float:
            return self.n >= self.convert_float(other).n
        return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.merge(other).n <= other.merge(self).n
        other_type = type(other)
        if other_type is int or other_type is bool:
            return self.n <= self.one * other
        elif other_type is float:
            return self.n <= self.convert_float(other).n
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.merge(other).n > other.merge(self).n
        other_type = type(other)
        if other_type is int or other_type is bool:
            return self.n > self.one * other
        elif other_type is float:
            return self.n > self.convert_float(other).n
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.merge(other).n < other.merge(self).n
        other_type = type(other)
        if other_type is int or other_type is bool:
            return self.n < self.one * other
        elif other_type is float:
            return self.n < self.convert_float(other).n
        return False

    @staticmethod
    def magnify_int(num, dp):
        if dp > 0 and num:
            return num * 10**dp
        return num

    @staticmethod
    def reduce_int(num, dp):
        if dp > 0 and num:
            return num // 10**dp
        return num

    def magnify_precision(self, dp):
        """放大整数，增加小数位数.
        如果新的小数位数小于原本，则什么都不做.
        """
        dp -= self.dp
        if dp > 0:
            self.dp += dp
            n = 10 ** dp
            if self.n:
                self.n *= n
            self.one *= n
        return None

    def reduce_precision(self, dp):
        """缩小整数，减少小数位数.
        如果新的小数位数大于原本，则什么都不做.
        """
        dp = self.dp - dp
        if dp > 0:
            self.dp -= dp
            n = 10 ** dp
            if self.n:
                self.n //= n
            self.one //= n
        return None

    def change_precision(self, dp):
        if self.dp < dp:
            self.magnify_precision(dp)
        elif self.dp > dp:
            self.reduce_precision(dp)
        return None

    def merge(self, obj):
        """将与另一个此类型对象合并成一个新对象."""
        new = self.copy()
        if obj.dp > new.dp:
            new.n *= 10 ** (obj.dp - new.dp)
            new.one = obj.one
            new.dp = obj.dp
        return new

    @classmethod
    def from_int(cls, n, precision=0):
        """将整数类型转换成此类型."""
        return cls(n, 0, precision)

    @classmethod
    def from_float(cls, n, precision=0):
        """将浮点类型转换成此类型."""
        return cls.from_str(str(n), precision)

    @classmethod
    def from_str(cls, n, precision=0):
        """将数字串转换成此类型."""
        n = convert_sn(n)
        dp = StrDecs(n)
        return cls(int(dp.floats2ints(n)), dp.dp, precision)

    def convert_int(self, n):
        """以自身为模板，将整数类型转换成此类型."""
        new = self.copy()
        new.n = n * new.one
        return new

    def convert_float(self, n):
        """以自身为模板，将浮点类型转换成此类型."""
        return self.convert_str(str(n))

    def convert_str(self, n):
        """以自身为模板，将数字串转换成此类型."""
        new = self.copy()
        n = convert_sn(n)
        dp = StrDecs(n)
        n = int(dp.floats2ints(n))
        new.n = new.one * n // 10 ** dp.dp
        return new

    def root(self, exponent=2) -> Decimal:
        """开根号."""
        if type(exponent) is float:
            exponent = self.from_float(exponent)
        if exponent == 0:
            new = self.copy()
            new.n = new.one
            return new
        elif exponent == 1:
            return self.copy()
        return root(self, exponent)  # type: ignore

    def separate(self):
        """分割整数和小数部分."""
        # integer = str(abs(self._n)).zfill(self.dp + 1)
        # return integer[:-self.dp], integer[-self.dp:]
        integer, decimals = divmod(abs(self.n), self.one)
        return int2str(integer), int2str(decimals).zfill(self.dp)

    def copy(self):
        new = self.__class__()
        new.__dict__ = self.__dict__.copy()
        return new

    def get_n(self):
        """获取内部存储的整数."""
        return self.n

    def get_one(self):
        return self.one

    def get_decimal_place(self):
        """获取小数位数."""
        return len(StrDecs.rstrip_zero(self.separate()[1]))

    def get_precision(self):
        """获取精度."""
        return self.dp

    def get_full(self):
        result = ".".join(self.separate())
        if self.n < 0:
            result = "-" + result
        return result


def main():
    n = Decimal.from_str("2", 5000)
    n.display_precision = 16
    a = n + 123.45
    b = n.root(2)
    print(2 + 123.45, 2 ** 0.5)
    print(a, b)
    print(a.get_full())
    print(b.get_full())


if __name__ == "__main__":
    main()
