import random as _random
import decimal as _decimal
import hashlib as _hashlib
import typing as _t

try:
    from .. import mathut as _mathut
except ImportError:
    from ahfakit import mathut as _mathut


def subsection_str(obj, k, right=False):
    """分段字符串."""
    if not obj:
        return None
    if right:
        index = divmod(len(obj), k)[1]
        if index:
            yield obj[:index]
            obj = obj[index:]
    while obj:
        yield obj[:k]
        obj = obj[k:]


class RSA(object):
    """RSA加密算法."""

    def __init__(self, n: int, e: int, d: int):
        self._n_len = 1
        self._n = 1
        self.n = n
        self.e = e
        self.d = d
        self.encoding = "UTF-8"

    @classmethod
    def generate_key(cls, digits=1024, e=None, pqk=2):
        """随机生成n、公钥、私钥.
        可指定公钥, 例如e=65537.
        返回n、公钥、私钥.
        digits 最好不小于 24.
        """
        while True:
            # 生成多个素数并计算fy_n和fy的值
            n, fy = cls.generate_n_fyn(digits, pqk)
            # 如果没有给出公钥则随机获取公钥
            if e is None:
                e = cls.generate_e(n, digits)
                break
            # 如果指定的e和n互质，退出循环，否则重新获取n, fy
            elif _mathut.gcd(n, e) == 1:
                break
        # 得到私钥
        d = cls.generate_d(fy, e)
        # 返回n, 公钥, 私钥
        return n, e, d

    @classmethod
    def generate_n_fyn(cls, digits, k=2):
        """随机生成n和fy."""
        n = fy = 1
        # 产生k个素数并计算n和fy
        for i in cls.random_prime(digits, k):
            n *= i
            fy *= i - 1
        return n, fy

    @classmethod
    def generate_e(cls, n, digits):
        """根据n随机创建公钥."""
        while True:
            # 随机生成素数并判断是否和n互质
            e = cls.random_prime(digits)[0]
            if _mathut.gcd(n, e) == 1:
                break
        return e

    @staticmethod
    def generate_d(fy, e):
        """根据公钥和fy获取一个私钥."""
        # 扩展欧里几得算法快速获取d
        d = _mathut.gcd_ext_euclid(fy, e)[1]
        if d < 0:
            d += fy
        return d

    @staticmethod
    def generate_d_list(fy, e, k=1, start=0):
        """生成一个或多个私钥.
        返回含d的列表, 和k值.
        """
        results = []
        i = start
        while len(results) < k:
            i += 1
            d = (i*fy + 1) / e
            d_int = int(d)
            if d == d_int and d_int not in results:
                results.append(d_int)
        return results, i

    @staticmethod
    def random_prime(digits, pq_count=1, k=None):
        """随机获取素数.

        Args:
            digits (int): 二进制位数
            pq_count (int, optional): 分成几份, 例如获取p, q, 值取2. Defaults to 1.
            k (int, optional): 获取几个素数, 默认为 pq_count. Defaults to None.
        """
        pos = 1
        if pq_count != 1:
            # 获取多个素数并合成
            _decimal.getcontext().prec = _mathut.predict_digits(digits)
            digits = _decimal.Decimal(str(digits)) / pq_count
            # 填补分多个素数合成带来的误差
            pos = 2**(_decimal.Decimal(str(pq_count)) - 1) / pq_count
        # 素数范围
        range_b = 2**digits
        range_a = range_b//2 * pos
        range_a, range_b = int(range_a), int(range_b - 1)

        results = []
        for _ in range(pq_count if k is None else k):
            while True:
                # 随机数
                result = _random.randint(range_a, range_b)
                if _mathut.is_prime(result) and result not in results:
                    results.append(result)
                    break
        return results

    @staticmethod
    def key_xor_hashpwd(key: _t.Tuple[int, int, int], password: _t.Union[str, bytes], digits: int = ...):
        """将 key 与密码异或"""
        if digits is ...:
            digits = int(len(str(key[0])) / 2.56)
        if isinstance(password, str):
            password = password.encode("ASCII")
        pwd_code = int(_hashlib.shake_128(password).hexdigest(digits), 16)
        return key[0] ^ pwd_code, key[1] ^ pwd_code, key[2] ^ pwd_code

    def encrypt(self, integer, e=None):
        """加密整数"""
        return pow(integer, self.e if e is None else e, self.n)

    def decrypt(self, integer, d=None):
        """解密整数"""
        return pow(integer, self.d if d is None else d, self.n)

    def encrypt_bytes(self, obj: bytes, e=None, hexadecimal=True):
        """加密字节"""
        s = str(int(obj.hex(), 16))
        # 分段加密字节
        result = ""
        for i in subsection_str(s, self._n_len - 1, right=True):
            result += str(self.encrypt(int(i), e)).zfill(self._n_len)
        # 转换十六进制
        if hexadecimal:
            result = hex(int(result))[2:]
        # 转换为字节
        result = result.encode("ASCII")
        return result

    def decrypt_bytes(self, obj: bytes, d=None, hexadecimal=True):
        """解密字节"""
        # 解析16进制
        s = str(int(obj, 16)) if hexadecimal else obj
        # 分段解密字符串
        result = ""
        for i in subsection_str(s, self._n_len, right=True):
            result += str(self.decrypt(int(i), d)).zfill(self._n_len - 1)
        # 还原字节
        result = hex(int(result))[2:]
        result = bytes.fromhex(result)
        return result

    def encrypt_str(self, obj: str, e=None, hexadecimal=True):
        """加密字符串"""
        # 转换为数字串
        obj = str(int(obj.encode(self.encoding).hex(), 16))
        # 分段加密字符串
        result = ""
        for i in subsection_str(obj, self._n_len - 1, right=True):
            result += str(self.encrypt(int(i), e)).zfill(self._n_len)
        # 转换十六进制
        if hexadecimal:
            result = hex(int(result))[2:]
        return result

    def decrypt_str(self, obj: str, d=None, hexadecimal=True):
        """解密字符串"""
        # 解析16进制
        if hexadecimal:
            obj = str(int(obj, 16))
        # 分段解密字符串
        result = ""
        for i in subsection_str(obj, self._n_len, right=True):
            result += str(self.decrypt(int(i), d)).zfill(self._n_len - 1)
        # 还原
        result = hex(int(result))[2:]
        result = bytes.fromhex(result).decode(self.encoding)
        return result

    def get_key(self):
        """获取n, e, d"""
        return self.n, self.e, self.d

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, value):
        self._n = value
        self._n_len = len(str(value))


def main():
    # n, e, d
    rsa = RSA(n=3189370259, e=3961537159, d=2672103319)
    print(rsa.get_key())
    # 原文
    text = "Hello World"
    # 密文
    encrypt = rsa.encrypt_str(text)
    print("密文:\t", encrypt)

    # 明文
    decrypt = rsa.decrypt_str(encrypt)
    print("明文:\t", decrypt)


if __name__ == "__main__":
    main()
