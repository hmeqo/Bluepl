__all__ = [
    # Round
    "ceil", "floor",

    # Power, modulus
    "pow", "powmod",

    # Root
    "enrt", "root", "newton_method", "dichotomy_root",

    # Factorial
    "factorial", "factorial_gen", "factorial_stirling",

    # Prime
    "prime", "is_prime", "primes", "prime_miller_rabin", "prime_factorization",

    # Formulas, Functions
    "gcd", "gcd_ext_euclid", "sin", "cos", "tan", "asin", "acos", "atan",
    "sin2", "cos2", "fib", "fib_nth",

    # Constants
    "pi", "e", "dec_pi", "dec_e", "dec_2", "prime_list_k",

    # formulas
    "binomial_theorem",
]

import math as _math
import decimal as _decimal
import random as _random
import typing as _t
from typing import Union as _Union

pi = _math.pi
e = _math.e

dec_pi = _decimal.Decimal(str(pi))
dec_e = _decimal.Decimal(str(e))
dec_2 = _decimal.Decimal('2')

# 一千以内所有素数
prime_list_k = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
    317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
    503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601,
    607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
    701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809,
    811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907,
    911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997,
)

prime_set_k = set(prime_list_k)


def ceil(num):
    """向上取整"""
    result = int(num)
    if result == num:
        return result
    return result + 1


def floor(num):
    """向下取整"""
    if isinstance(num, int):
        return num
    return int(num // 1)


def pow(n, e: int):
    result = 1
    while e:
        if e & 1:
            result *= n
        n *= n
        e >>= 1
    return result


@_t.overload
def powmod(n: int, e: int, m: int) -> int: ...


@_t.overload
def powmod(n: float, e: int, m: float) -> float: ...


def powmod(n, e, m):
    """幂取模"""
    n %= m
    result = 1
    while e:
        if e & 1:
            result = (result * n) % m
        n = (n * n) % m
        e >>= 1
    return result


def enrt(func, n, exponent: _Union[int, float] = 2, *args, **kwargs):
    """丰富根号计算结果"""
    # 指数为0返回1
    if exponent == 0:
        return 1
    # 指数为1返回这个数本身
    elif exponent == 1:
        return n

    # 底数指数是否是负数
    n_is_neg = n < 0
    exponent_is_neg = exponent < 0

    # 如果底数是负数
    if n_is_neg:
        # 如果指数是小数或是偶数，则涉及复数计算
        if isinstance(exponent, float) or not exponent & 1:
            return complex(n) ** (1 / complex(exponent))
        # 先取正数，最后再改回负数
        else:
            n = abs(n)
    # 如果指数是负数，n取倒数，指数取正数
    if exponent_is_neg:
        n = 1 / n
        exponent = abs(exponent)

    # 计算
    result = func(n, exponent, *args, **kwargs)

    # 如果n原本是负数, 取负数
    if n_is_neg:
        result = -result
    return result


def newton_method(n, exponent: _Union[int, float] = 2):
    """牛顿迭代法"""
    x0 = 1
    e0 = exponent - 1
    _a = x0
    x_n = x0 + (n/x0**e0 - x0)/exponent
    while _a != x_n:
        _a = x0
        x0 = x_n
        x_n = x0 + (n/x0**e0 - x0)/exponent if x0 else x0
    return x_n


def dichotomy_root(n, exponent: _Union[int, float] = 2):
    """二分法"""
    low = 0
    high = n
    a = n
    result = 0
    while result != a:
        a = result
        result = (low + high) / 2
        b = result ** exponent
        if b > n:
            high = result
        elif b < n:
            low = result
    return result


def factorial(n: int, double=False):
    """阶乘, 可计算双阶乘."""
    result = 1
    if not double:
        '''
        计算 n 整除和取余 2 的值
        如果没有余数, result 乘以 n 减一的双阶乘
        如果有余数, result 乘以 n 的双阶乘
        将 n 整除 2 的结果赋值给 n
        result 乘以 2 的 n 次方
        不断循环以上步骤, 直到 n 等于 1
        '''
        pw2 = 0
        while n > 1:
            a = divmod(n, 2)
            result *= factorial(n if a[1] else n - 1, True)
            n = a[0]
            pw2 += n
        result <<= pw2
    else:
        for i in range(n, 1, -2):
            result *= i
    return result


def factorial_gen(n: int):
    yield 1
    result = 1
    for i in range(1, n + 1):
        result *= i
        yield result


def factorial_stirling(n):
    """斯特林公式.
    斯特林公式: 取 n 的阶乘的近似值的数学公式.
    """
    n = _decimal.Decimal(str(n))
    return round(root(dec_2 * dec_pi * n) * (n / dec_e)**n)


def prime(n: int, stop=None):
    """n 是否是质数，可指定返回范围内的质数 n ~ stop(不包含stop)."""
    if not stop:
        return is_prime(n)
    result = [2] if n <= 2 else []
    # 偶数加一
    if not n & 1:
        n += 1
    # 此部分负责小于1001的数
    start_index = None
    end_index = None
    for index, i in enumerate(prime_list_k):
        if start_index is None:
            if i >= n:
                start_index = index
        elif i >= stop:
            end_index = index
            break
    if start_index:
        result.extend(prime_list_k[start_index:end_index])
    # 此部分负责大于等于1001的数
    if stop > 1001:
        for x in range(1001, stop, 2):
            if prime_miller_rabin(x):
                result.append(x)
    return result


def is_prime(n: int):
    if not n & 1:
        return False
    if n <= 1000:
        return n in prime_set_k
    for i in prime_list_k:
        if not n % i:
            return False
    return prime_miller_rabin(n)


def primes(n: int):
    """Returns a list of primes < n"""
    half_n = n // 2
    sieve = [True] * half_n
    for i in range(3, int(n ** 0.5) + 1, 2):
        if sieve[i//2]:
            sieve[i*i//2::i] = [False] * ((n - i*i - 1)//(2 * i) + 1)
    return [2] + [2*i + 1 for i in range(1, half_n) if sieve[i]]


def prime_miller_rabin(num: int):
    """判断一个数是否是质数，这个数不能太小."""
    s = num - 1
    t = 0
    while s & 1 == 0:
        s = s // 2
        t += 1

    for _ in range(5):
        a = _random.randrange(2, num - 1)
        v = powmod(a, s, num)
        if v != 1:
            i = 0
            while v != num - 1:
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = v**2 % num
    return True


def prime_factorization(num: int):
    """质因数分解."""
    result = []
    while not num % 2:
        num //= 2
        result.append(2)
    i = 3
    while i <= num:
        if num % i:
            i += 2
            continue
        num //= i
        result.append(i)
    return result


def gcd(a, b):
    """最大公约数"""
    while a != 0:
        a, b = b % a, a
    return b


def gcd_ext_euclid(a, b):
    """最大公约数.
    扩展欧里几得算法.
    ax + by = gcd(a, b).
    返回 x, y, q.(q为最大公约数)
    """
    # 递
    lst = [(a, b)]
    a, b = lst[0]
    while True:
        if b == 0:
            break
        else:
            a, b = b, a % b
            lst.append((a, b))
    # 归
    del lst[-1]
    x, y, q = 1, 0, a
    while lst:
        a, b = lst.pop()
        x, y = y, x - (a // b)*y
    return x, y, q


def sin(angle):
    return _math.sin(angle * pi / 180)


def cos(angle):
    return _math.cos(angle * pi / 180)


def tan(angle):
    return _math.tan(angle * pi / 180)


def asin(ratio):
    return _math.asin(ratio) * 180 / pi


def acos(ratio):
    return _math.acos(ratio) * 180 / pi


def atan(ratio):
    return _math.atan(ratio) * 180 / pi


def sin2(x, angle=False):
    # sin x = x - x^3/3! + x^5/5! - x^7/7! + ... + (-1)^n-1 x^(2n-1)/(2n-1)!
    if angle:
        x = x * pi / 180
    result = x
    sign = 1
    x_e = x
    j = 1
    f = 1
    i = 1
    while f:
        i += 2
        sign *= -1
        x_e *= x * x
        j *= i * (i - 1)
        f = sign * x_e / j
        result += f
    return result


def cos2(x, angle=False):
    if angle:
        x = x * pi / 180
    result = pi/2 - x
    sign = 1
    x_e = x
    j = 1
    f = 1
    i = 1
    while f:
        i += 2
        sign *= -1
        x_e *= x * x
        j *= i * (i - 1)
        f = sign * x_e / j
        result += f
    return result


def fib(n: int):
    a, b = 0, 1
    while a < n:
        yield a
        a, b = b, a + b


def fib_nth(n: int):
    if n >= 2:
        a, b = 0, 1
        yield a
        for _ in range(1, n):
            a, b = b, a + b
            yield a
    elif n == 1:
        yield 1
    elif n == 0:
        yield 0


def binomial_theorem(x, y, n=2):
    """二项式定理 $(x+y)^n$"""
    fac_n = factorial(n)
    return sum(fac_n / (k_fac * factorial(n - k)) * x**(n-k) * y**(k)
               for k_fac, k in zip(factorial_gen(n + 1), range(n + 1)))


root = newton_method
