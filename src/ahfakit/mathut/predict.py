def predict_digits(bit_digits: int) -> int:
    """预测二进制长度对应的十进制长度"""
    # w = 0.3010281762631502
    # b = 0.5015807409259041
    w = 0.3010281762263712
    b = 0.5015807678542549
    y = w*bit_digits + b
    return round(y)
    # return int(y)


def main():
    a = []
    for i in range(1, 2048 + 1):
        pre = predict_digits(i) == len(str(2**i))
        print(i, pre)
        a.append(pre)
    print("失误次数:", a.count(False))


if __name__ == "__main__":
    main()
