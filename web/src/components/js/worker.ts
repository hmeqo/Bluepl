import vueWorker from 'simple-web-worker'

export default vueWorker?.create([
    {
        message: 'session',
        func: (key?: bigint, e?: bigint, p?: bigint) => {
            const one: bigint = BigInt(1)

            const prime_list_k: bigint[] = []

            const _prime_list_k = [
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
            ]

            for (const i in _prime_list_k) {
                prime_list_k.push(BigInt(_prime_list_k[i]))
            }

            const prime_set_k: Set<bigint> = new Set(prime_list_k)

            /** 判断是否质数 */
            function isPrime(n: bigint) {
                if (!(n & one)) {
                    return false
                }
                if (n <= BigInt(1000)) {
                    return prime_set_k.has(n)
                }
                for (const i in prime_list_k) {
                    if (!(n % prime_list_k[i])) {
                        return false
                    }
                }
                return primeMillerRabin(n)
            }

            /** Miller Rabin 算法判断质数 */
            function primeMillerRabin(num: bigint) {
                var s = num - one
                var t = 0
                while ((s & one) == BigInt(0)) {
                    s = s / BigInt(2)
                    t++
                }
                for (var i = 0; i < 5; i++) {
                    var a = getRandBigInt(BigInt(2), num - one)
                    var v = powmod(a, s, num)
                    if (v != one) {
                        i = 0
                        while (v != num - one) {
                            if (i == t - 1) {
                                return false
                            } else {
                                i = i + 1
                                v = v * v % num
                            }
                        }
                    }
                }
                return true
            }

            /** 获取随机素数 */
            function getRandPrime(bitLength: bigint) {
                var range_b = pow(BigInt(2), bitLength)
                var range_a = range_b >> one
                range_b--
                while (true) {
                    var num = getRandBigInt(range_a, range_b)
                    if (isPrime(num)) {
                        return num
                    }
                }
            }

            function pow(n: bigint, e: bigint) {
                var result = one
                while (e) {
                    if (e & one) {
                        result *= n
                    }
                    n *= n
                    e = e >> one
                }
                return result
            }

            /** 幂的模 */
            function powmod(n: bigint, e: bigint, m: bigint) {
                n %= m
                var result = one
                while (e) {
                    if (e & one) {
                        result = (result * n) % m
                    }
                    n = (n * n) % m
                    e = e >> one
                }
                return result
            }

            /** 任意长度随机bit数组 */
            function getRandbits(k: number) {
                var result: number[] = new Array(k)
                for (var i = 0; i < k; i++) {
                    result[i] = Math.floor(Math.random() * 2)
                }
                return result
            }

            /** BigInt 转bit数组 */
            function BigIntToBits(num: bigint) {
                var result: number[] = []
                while (num) {
                    result.push(Number(num & one))
                    num = num >> one
                }
                return result.reverse()
            }

            /** bit数组转 BigInt */
            function bitsToBigInt(bits: number[]) {
                var result = BigInt(0)
                for (var i = 0; i < bits.length; i++) {
                    if (bits[i]) {
                        result += pow(BigInt(2), BigInt(i))
                    }
                }
                return result
            }

            /** 任意大小的随机整数, 包含 start 和 stop */
            function getRandBigInt(start: bigint, stop: bigint) {
                var bitLength = BigIntToBits(stop - start).length
                var randbits: number[]
                do {
                    randbits = getRandbits(bitLength)
                } while (randbits[0] > bitLength[0])
                return start + bitsToBigInt(randbits)
            }

            if (key && e && p) {
                return powmod(key, e, p)
            } else {
                let p = getRandPrime(BigInt(1024))
                let g = getRandBigInt(p >> one, p - one)
                let e = getRandBigInt(p >> one, p - one)
                let key = powmod(g, e, p)
                return { p, g, e, key }
            }
        }
    }
])
