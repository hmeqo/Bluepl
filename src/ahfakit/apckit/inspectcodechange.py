import hashlib
import inspect
import re
import types as _types


DEFAULT_SIZE = 1000


def get_frame_vc(frame: _types.FrameType, size=DEFAULT_SIZE):
    """获取frame的vc"""
    return get_vc(inspect.getsource(frame), size)


def get_vc(s: str, size=DEFAULT_SIZE):
    """获取str的vc"""
    return int(hashlib.sha256(s.encode()).hexdigest(), 16) % size


def force_vc(frame, size=DEFAULT_SIZE):
    """穷举出一个vc"""
    b = inspect.getsource(frame)
    span = re.search(r"(?<=%s\()\d+" % inspectcodechange.__name__, b)
    if span:
        left, right = b[:span.start()], b[span.end():]
        for i in range(size):
            code = left + str(i) + right
            vc = get_vc(code)
            if vc == i:
                return i
    return None


def inspectcodechange(vc):
    """检查vc"""
    frame = inspect.getouterframes(inspect.currentframe())[1].frame
    frame_code = inspect.getsource(frame)
    return vc == get_vc(frame_code)


def main(n=10):
    if inspectcodechange(7):
        print("验证成功")
    else:
        print("验证失败, 我的代码被修改了")
        return 0  # 整个bug
    return 2**n


if __name__ == "__main__":
    # print(force_vc(main))
    print(main())
