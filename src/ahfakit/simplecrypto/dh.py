import random

try:
    from .. import mathut as _mathut
except ImportError:
    from ahfakit import mathut as _mathut


class DH(object):

    def __init__(self, p: int, g: int, e: int):
        # 质数
        self.p = p
        # 整数
        self.g = g
        # 私钥
        self.e = e

    @staticmethod
    def generate_p(bits: int):
        """随机质数"""
        range_b = 2**bits
        range_a = range_b >> 1
        range_b -= 1
        while True:
            num = random.randint(range_a, range_b)
            if _mathut.is_prime(num):
                return num

    @staticmethod
    def generate_g(p: int):
        """根据p的大小生成随机整数"""
        return random.randint(p >> 1, p - 1)

    def step1(self):
        return pow(self.g, self.e, self.p)

    def step2(self, n: int):
        """和对方的公钥合成密钥"""
        return pow(n, self.e, self.p)

    randint = random.randint


def main():
    bits = 2048
    p = DH.generate_p(bits)
    g = DH.generate_g(p)

    ea = DH.randint(p >> 1, p)
    eb = DH.randint(p >> 1, p)

    dh1 = DH(p, g, ea)
    dh2 = DH(p, g, eb)

    ya = dh1.step1()
    yb = dh2.step1()

    ka = dh1.step2(yb)
    kb = dh2.step2(ya)
    print(ka, kb)


if __name__ == "__main__":
    main()
