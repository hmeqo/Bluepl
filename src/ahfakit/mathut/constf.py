import multiprocessing
import os as _os
import math as _math

from . import mathut as _mathut
try:
    from .. import progressbar as _pgb
except ModuleNotFoundError:
    pass


def _sort_list(lst, count, si=0):
    """拌匀列表元素.

    Arguments:
        params : list : 列表
        count : int : 多少元素视作一个单位，按照这个单位排序
        si : int : 起始排序位置
    """
    lst_len = len(lst)
    sort_len = lst_len - si
    if sort_len > 2:
        sort_len = lst_len - lst_len % count
        mid_index = sort_len//2
        mid_index = mid_index - mid_index % count + si
        sort_len += si
        for i, i2 in zip(
                range(si, mid_index, count*2),
                range(sort_len, mid_index + 1, -count*2)):
            lst[i:i+count], lst[i2-count:i2] = lst[i2-count:i2], lst[i:i+count]


class Pi(object):

    pgb_config = {}
    k = 10

    @classmethod
    def prec(cls, precision=16) -> int:
        k = cls.k + len(str(precision)) + 1
        pre = precision + k
        b = 10 ** pre
        x1 = b * 4 // 5
        x2 = b // -239
        s1 = -25
        s2 = -57121
        result = x1 + x2

        n = int(pre * 1.5)
        for i in range(3, n, 2):
            x1 //= s1
            x2 //= s2
            x = (x1 + x2) // i
            if x == 0:
                break
            result += x
        result = result * 4 // 10**k
        return result

    @classmethod
    def ramanujan(cls, n: int, is_prec=True, space_for_time=False) -> int:
        """Ramanujan formulas.

        WARNING: is used multiprocessing,
        please write in `if __name__ == __main__`.
        """
        cpu_count = _os.cpu_count()
        assert isinstance(cpu_count, int)
        with multiprocessing.Pool(processes=cpu_count) as pool:
            valid_digits = 14
            if is_prec:
                iter_count = n / valid_digits
                if iter_count % 1:
                    iter_count += 1
                iter_count = int(iter_count)
            else:
                iter_count = n
            prec = valid_digits * iter_count

            result = _mathut.Decimal(0, 0, prec + cls.k)
            count = 4 * cpu_count
            bar = _pgb.ProgressBar(total=iter_count, **cls.pgb_config)

            if space_for_time:
                ftrs = [i for i in _mathut.factorial_gen(6 * iter_count)]
                params = [(i, result, (ftrs[i], ftrs[3*i], ftrs[6*i]))
                          for i in range(iter_count)]
                del ftrs
                # 对参数排序，使进度条过渡更平滑
                _sort_list(params, cpu_count)
                bar.start()
                while params:
                    result += sum(pool.map(cls._ramanujan2, params[:count]))
                    bar.add_progress(len(params[:count]))
                    del params[:count]
            else:
                params = [(i, result) for i in range(iter_count)]
                _sort_list(params, cpu_count)
                bar.start()
                while params:
                    result += sum(pool.map(cls._ramanujan, params[:count]))
                    bar.add_progress(len(params[:count]))
                    del params[:count]

        bar.fill_up()
        bar.wait(1)

        bar.total = 1
        bar.start()

        result = 426880 * result.convert_int(10005).root(2) / result
        result = result.n // 10**(result.dp-(n if is_prec else prec))

        bar.fill_up()
        bar.wait(1)

        return result

    @staticmethod
    def _ramanujan(k):
        k, dec_ = k
        return (
            dec_.convert_int(_math.factorial(6 * k) * (13591409 + 545140134*k))
            / (_math.factorial(3 * k)
               * _math.factorial(k)**3
               * (-640320)**(3 * k)))

    @staticmethod
    def _ramanujan2(k):
        k, dec_, ftrs = k
        return (dec_.convert_int(ftrs[2] * (13591409 + 545140134*k))
                / (ftrs[1] * ftrs[0]**3 * (-640320)**(3 * k)))

    @classmethod
    def machin(cls, precision=16) -> int:
        """马青公式 (内置进度条)."""
        print("\n初始化变量...", end="")
        # 多计算k位，防止尾数取舍的影响
        k = cls.k + len(str(precision)) + 1
        pre = precision + k
        b = 10 ** pre
        # 求含4/5的首项
        # 求含1/239的首项
        x1 = b * 4 // 5
        x2 = b // -239
        # x1 = b * 16 // 5
        # x2 = b * 4 // -239
        s1 = -25
        s2 = -57121
        # 求第一大项
        result = x1 + x2

        # 设置下面循环的终点，即共计算n项
        n = int(2 * pre * 0.75)
        # 启动进度条
        bar = _pgb.ProgressBar(total=n + 2, **cls.pgb_config)
        bar.start()
        # 循环初值=3，末值2n,步长=2
        for i in range(3, n, 2):
            # 求每个含1/5的项及符号
            x1 //= s1
            # 求每个含1/239的项及符号
            x2 //= s2
            # 求两项之和
            x = (x1 + x2) // i
            if x == 0:
                break
            # 求总和
            result += x
            bar.progress = i
        # 求出π 并 舍掉后k位
        # result //= 10 ** k
        result = result * 4 // 10**k

        bar.fill_up()
        bar.wait(1)
        return result


class E(object):

    pgb_config = {}
    k = 10

    @classmethod
    def taylor(cls, precision=16) -> int:
        """Taylor formulas.

        WARNING: is used multiprocessing,
        """
        # 计算时的精度
        p1 = precision + len(str(precision)) + cls.k
        # 迭代次数，精度越高，此数值越小
        if p1 < 100:
            # p1 < 100
            p2 = p1
        elif p1 < 500:
            # 100 <= p1 < 500
            p2 = 65 * p1 // 100
        elif p1 < 1000:
            # 500 <= p1 < 1000
            p2 = 50 * p1 // 100
        elif p1 < 5000:
            # 1000 <= p1 < 5000
            p2 = 45 * p1 // 100
        elif p1 < 10000:
            # 5000 <= p1 < 10000
            p2 = 36 * p1 // 100
        elif p1 < 100000:
            # 10000 <= p1 < 100000
            p2 = 33 * p1 // 100
        else:
            # 100000 <= p1
            p2 = 30 * p1 // 100

        cpu_count = _os.cpu_count()
        assert isinstance(cpu_count, int)
        with multiprocessing.Pool(processes=cpu_count) as pool:
            bar = _pgb.ProgressBar(**cls.pgb_config)

            result = _mathut.Decimal(0, 0, p1)
            one = result.convert_int(1)
            count = 64 * cpu_count

            params = [(one, i) for i in _mathut.factorial_gen(p2)]
            _sort_list(params, count)
            bar.total = len(params)
            bar.start()
            while params:
                result += sum(pool.map(cls._taylor, params[:count]))
                bar.add_progress(len(params[:count]))
                del params[:count]

        bar.fill_up()
        bar.wait(1)
        return result.n // 10**(result.dp-precision)

    @staticmethod
    def _taylor(k):
        return k[0] / k[1]
