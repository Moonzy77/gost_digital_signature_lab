import os
import random


BLOCK_SIZE = 64
ZERO_512 = bytes(BLOCK_SIZE)
BLOCK_BITS = (512).to_bytes(BLOCK_SIZE, "big")
IV_256 = bytes([1] * BLOCK_SIZE)
INFINITY = None


# Параметры хэш-функции ГОСТ Р 34.11-2012 (Стрибог)
PI = [
    0xFC, 0xEE, 0xDD, 0x11, 0xCF, 0x6E, 0x31, 0x16, 0xFB, 0xC4, 0xFA, 0xDA, 0x23, 0xC5, 0x04, 0x4D,
    0xE9, 0x77, 0xF0, 0xDB, 0x93, 0x2E, 0x99, 0xBA, 0x17, 0x36, 0xF1, 0xBB, 0x14, 0xCD, 0x5F, 0xC1,
    0xF9, 0x18, 0x65, 0x5A, 0xE2, 0x5C, 0xEF, 0x21, 0x81, 0x1C, 0x3C, 0x42, 0x8B, 0x01, 0x8E, 0x4F,
    0x05, 0x84, 0x02, 0xAE, 0xE3, 0x6A, 0x8F, 0xA0, 0x06, 0x0B, 0xED, 0x98, 0x7F, 0xD4, 0xD3, 0x1F,
    0xEB, 0x34, 0x2C, 0x51, 0xEA, 0xC8, 0x48, 0xAB, 0xF2, 0x2A, 0x68, 0xA2, 0xFD, 0x3A, 0xCE, 0xCC,
    0xB5, 0x70, 0x0E, 0x56, 0x08, 0x0C, 0x76, 0x12, 0xBF, 0x72, 0x13, 0x47, 0x9C, 0xB7, 0x5D, 0x87,
    0x15, 0xA1, 0x96, 0x29, 0x10, 0x7B, 0x9A, 0xC7, 0xF3, 0x91, 0x78, 0x6F, 0x9D, 0x9E, 0xB2, 0xB1,
    0x32, 0x75, 0x19, 0x3D, 0xFF, 0x35, 0x8A, 0x7E, 0x6D, 0x54, 0xC6, 0x80, 0xC3, 0xBD, 0x0D, 0x57,
    0xDF, 0xF5, 0x24, 0xA9, 0x3E, 0xA8, 0x43, 0xC9, 0xD7, 0x79, 0xD6, 0xF6, 0x7C, 0x22, 0xB9, 0x03,
    0xE0, 0x0F, 0xEC, 0xDE, 0x7A, 0x94, 0xB0, 0xBC, 0xDC, 0xE8, 0x28, 0x50, 0x4E, 0x33, 0x0A, 0x4A,
    0xA7, 0x97, 0x60, 0x73, 0x1E, 0x00, 0x62, 0x44, 0x1A, 0xB8, 0x38, 0x82, 0x64, 0x9F, 0x26, 0x41,
    0xAD, 0x45, 0x46, 0x92, 0x27, 0x5E, 0x55, 0x2F, 0x8C, 0xA3, 0xA5, 0x7D, 0x69, 0xD5, 0x95, 0x3B,
    0x07, 0x58, 0xB3, 0x40, 0x86, 0xAC, 0x1D, 0xF7, 0x30, 0x37, 0x6B, 0xE4, 0x88, 0xD9, 0xE7, 0x89,
    0xE1, 0x1B, 0x83, 0x49, 0x4C, 0x3F, 0xF8, 0xFE, 0x8D, 0x53, 0xAA, 0x90, 0xCA, 0xD8, 0x85, 0x61,
    0x20, 0x71, 0x67, 0xA4, 0x2D, 0x2B, 0x09, 0x5B, 0xCB, 0x9B, 0x25, 0xD0, 0xBE, 0xE5, 0x6C, 0x52,
    0x59, 0xA6, 0x74, 0xD2, 0xE6, 0xF4, 0xB4, 0xC0, 0xD1, 0x66, 0xAF, 0xC2, 0x39, 0x4B, 0x63, 0xB6,
]

TAU = [
    0, 8, 16, 24, 32, 40, 48, 56,
    1, 9, 17, 25, 33, 41, 49, 57,
    2, 10, 18, 26, 34, 42, 50, 58,
    3, 11, 19, 27, 35, 43, 51, 59,
    4, 12, 20, 28, 36, 44, 52, 60,
    5, 13, 21, 29, 37, 45, 53, 61,
    6, 14, 22, 30, 38, 46, 54, 62,
    7, 15, 23, 31, 39, 47, 55, 63,
]

A_MATRIX = [
    0x8E20FAA72BA0B470, 0x47107DDD9B505A38, 0xAD08B0E0C3282D1C, 0xD8045870EF14980E,
    0x6C022C38F90A4C07, 0x3601161CF205268D, 0x1B8E0B0E798C13C8, 0x83478B07B2468764,
    0xA011D380818E8F40, 0x5086E740CE47C920, 0x2843FD2067ADEA10, 0x14AFF010BDD87508,
    0x0AD97808D06CB404, 0x05E23C0468365A02, 0x8C711E02341B2D01, 0x46B60F011A83988E,
    0x90DAB52A387AE76F, 0x486DD4151C3DFDB9, 0x24B86A840E90F0D2, 0x125C354207487869,
    0x092E94218D243CBA, 0x8A174A9EC8121E5D, 0x4585254F64090FA0, 0xACCC9CA9328A8950,
    0x9D4DF05D5F661451, 0xC0A878A0A1330AA6, 0x60543C50DE970553, 0x302A1E286FC58CA7,
    0x18150F14B9EC46DD, 0x0C84890AD27623E0, 0x0642CA05693B9F70, 0x0321658CBA93C138,
    0x86275DF09CE8AAA8, 0x439DA0784E745554, 0xAFC0503C273AA42A, 0xD960281E9D1D5215,
    0xE230140FC0802984, 0x71180A8960409A42, 0xB60C05CA30204D21, 0x5B068C651810A89E,
    0x456C34887A3805B9, 0xAC361A443D1C8CD2, 0x561B0D22900E4669, 0x2B838811480723BA,
    0x9BCF4486248D9F5D, 0xC3E9224312C8C1A0, 0xEFFA11AF0964EE50, 0xF97D86D98A327728,
    0xE4FA2054A80B329C, 0x727D102A548B194E, 0x39B008152ACB8227, 0x9258048415EB419D,
    0x492C024284FBAEC0, 0xAA16012142F35760, 0x550B8E9E21F7A530, 0xA48B474F9EF5DC18,
    0x70A6A56E2440598E, 0x3853DC371220A247, 0x1CA76E95091051AD, 0x0EDD37C48A08A6D8,
    0x07E095624504536C, 0x8D70C431AC02A736, 0xC83862965601DD1B, 0x641C314B2B8EE083,
]

C_CONSTANTS = [
    bytes.fromhex("b1085bda1ecadae9ebcb2f81c0657c1f2f6a76432e45d016714eb88d7585c4fc4b7ce09192676901a2422a08a460d31505767436cc744d23dd806559f2a64507"),
    bytes.fromhex("6fa3b58aa99d2f1a4fe39d460f70b5d7f3feea720a232b9861d55e0f16b501319ab5176b12d699585cb561c2db0aa7ca55dda21bd7cbcd56e679047021b19bb7"),
    bytes.fromhex("f574dcac2bce2fc70a39fc286a3d843506f15e5f529c1f8bf2ea7514b1297b7bd3e20fe490359eb1c1c93a376062db09c2b6f443867adb31991e96f50aba0ab2"),
    bytes.fromhex("ef1fdfb3e81566d2f948e1a05d71e4dd488e857e335c3c7d9d721cad685e353fa9d72c82ed03d675d8b71333935203be3453eaa193e837f1220cbebc84e3d12e"),
    bytes.fromhex("4bea6bacad4747999a3f410c6ca923637f151c1f1686104a359e35d7800fffbdbfcd1747253af5a3dfff00b723271a167a56a27ea9ea63f5601758fd7c6cfe57"),
    bytes.fromhex("ae4faeae1d3ad3d96fa4c33b7a3039c02d66c4f95142a46c187f9ab49af08ec6cffaa6b71c9ab7b40af21f66c2bec6b6bf71c57236904f35fa68407a46647d6e"),
    bytes.fromhex("f4c70e16eeaac5ec51ac86febf240954399ec6c7e6bf87c9d3473e33197a93c90992abc52d822c3706476983284a05043517454ca23c4af38886564d3a14d493"),
    bytes.fromhex("9b1f5b424d93c9a703e7aa020c6e41414eb7f8719c36de1e89b4443b4ddbc49af4892bcb929b069069d18d2bd1a5c42f36acc2355951a8d9a47f0dd4bf02e71e"),
    bytes.fromhex("378f5a541631229b944c9ad8ec165fde3a7d3a1b258942243cd955b7e00d0984800a440bdbb2ceb17b2b8a9aa6079c540e38dc92cb1f2a607261445183235adb"),
    bytes.fromhex("abbedea680056f52382ae548b2e4f3f38941e71cff8a78db1fffe18a1b3361039fe76702af69334b7a1e6c303b7652f43698fad1153bb6c374b4c7fb98459ced"),
    bytes.fromhex("7bcd9ed0efc889fb3002c6cd635afe94d8fa6bbbebab076120018021148466798a1d71efea48b9caefbacd1d7d476e98dea2594ac06fd85d6bcaa4cd81f32d1b"),
    bytes.fromhex("378ee767f11631bad21380b00449b17acda43c32bcdf1d77f82012d430219f9b5d80ef9d1891cc86e71da4aa88e12852faf417d5d9b21b9948bc924af11bd720"),
]


# Стандартные параметры кривой для обычной работы программы.
STANDARD_CURVE = {
    "name": "Standard",
    "p": int("8000000000000000000000000000000000000000000000000000000000000431", 16),
    "a": int("7", 16),
    "b": int("5FBFF498AA938CE739B8E022FBAFEF40563F6E6A3472FC2A514C0CE9DAE23B7E", 16),
    "q": int("8000000000000000000000000000000150FE8A1892976154C59CFC193ACCF5B3", 16),
    "gx": int("2", 16),
    "gy": int("08E2A8A0E65147D4BD6316030E16D19C85C97F0A9CA267122B96ABBCEA7E8FC8", 16),
}

# Контрольный пример 1 из ГОСТ Р 34.10-2012.
GOST_EXAMPLE_1 = {
    "name": "Пример 1 из ГОСТ Р 34.10-2012",
    "curve": {
        "name": "GOST-example-1",
        "p": int("8000000000000000000000000000000000000000000000000000000000000431", 16),
        "a": int("7", 16),
        "b": int("5FBFF498AA938CE739B8E022FBAFEF40563F6E6A3472FC2A514C0CE9DAE23B7E", 16),
        "q": int("8000000000000000000000000000000150FE8A1892976154C59CFC193ACCF5B3", 16),
        "gx": int("2", 16),
        "gy": int("08E2A8A0E65147D4BD6316030E16D19C85C97F0A9CA267122B96ABBCEA7E8FC8", 16),
    },
    "d": int("7A929ADE789BB9BE10ED359DD39A72C11B60961F49397EEE1D19CE9891EC3B28", 16),
    "e": int("2DFBC1B372D89A1188C09C52E0EEC61FCE52032AB1022E8E67ECE6672B043EE5", 16),
    "k": int("77105C9B20BCD3122823C8CF6FCC7B956DE33814E95B7FE64FED924594DCEAB3", 16),
    "qx": int("7F2B49E270DB6D90D8595BEC458B50C58585BA1D4E9B788F6689DBD8E56FD80B", 16),
    "qy": int("26F1B489D6701DD185C8413A977B3CBBAF64D1C593D26627DFFB101A87FF77DA", 16),
    "cx": int("41AA28D2F1AB148280CD9ED56FEDA41974053554A42767B83AD043FD39DC0493", 16),
    "cy": int("489C375A9941A3049E33B34361DD204172AD98C3E5916DE27695D22A61FAE46E", 16),
    "r": int("41AA28D2F1AB148280CD9ED56FEDA41974053554A42767B83AD043FD39DC0493", 16),
    "s": int("1456C64BA4642A1653C235A98A60249BCD6D3F746B631DF928014F6C5BF9C40", 16),
    "v": int("271A4EE429F84EBC423E388964555BB29D3BA53C7BF945E5FAC8F381706354C2", 16),
    "z1": int("5358F8FFB38F7C09ABC782A2DF2A3927DA4077D07205F763682F3A76C9019B4F", 16),
    "z2": int("03221B4FBBF6D101074EC14AFAC2D4F7EFAC4CF9FEC1ED11BAE336D27D527665", 16),
}

GOST_EXAMPLE_2 = {
    "name": "Пример 2 из ГОСТ Р 34.10-2012",
    "curve": {
        "name": "GOST-example-2",
        "p": int("4531ACD1FE0023C7550D267B6B2FEE80922B14B2FFB90F04D4EB7C09B5D2D15DF1D852741AF4704A0458047E80E4546D35B8336FAC224DD81664BBF528BE6373", 16),
        "a": int("7", 16),
        "b": int("1CFF0806A31116DA29D8CFA54E57EB748BC5F377E49400FDD788B649ECA1AC4361834013B2AD7322480A89CA58E0CF74BC9E540C2ADD6897FAD0A3084F302ADC", 16),
        "q": int("4531ACD1FE0023C7550D267B6B2FEE80922B14B2FFB90F04D4EB7C09B5D2D15DA82F2D7ECB1DBAC719905C5EECC423F1D86E25EDBE23C595D644AAF187E6E6DF", 16),
        "gx": int("24D19CC64572EE30F396BF6EBBFD7A6C5213B3B3D7057CC825F91093A68CD762FD60611262CD838DC6B60AA7EEE804E28BC849977FAC33B4B530F1B120248A9A", 16),
        "gy": int("2BB312A43BD2CE6E0D020613C857ACDDCFBF061E91E5F2C3F32447C259F39B2C83AB156D77F1496BF7EB3351E1EE4E43DC1A18B91B24640B6DBB92CB1ADD371E", 16),
    },
    "d": int("0BA6048AADAE241BA40936D47756D7C93091A0E8514669700EE7508E508B102072E8123B2200A0563322DAD2827E2714A2636B7BFD18AADFC62967821FA18DD4", 16),
    "e": int("3754F3CFACC9E0615C4F4A7C4D8DAB531B09B6F9C170C533A71D147035B0C5917184EE536593F4414339976C647C5D5A407ADEDB1D560C4FC6777D2972075B8C", 16),
    "k": int("0359E7F4B1410FEACC570456C6801496946312120B39D019D455986E364F365886748ED7A44B3E794434006011842286212273A6D14CF70EA3AF71BB1AE679F1", 16),
    "qx": int("115DC5BC96760C7B48598D8AB9E740D4C4A85A65BE33C1815B5C320C854621DD5A515856D13314AF69BC5B924C8B4DDFF75C45415C1D9DD9DD33612CD530EFE1", 16),
    "qy": int("37C7C90CD40B0F5621DC3AC1B751CFA0E2634FA0503B3D52639F5D7FB72AFD61EA199441D943FFE7F0C70A2759A3CDB84C114E1F9339FDF27F35ECA93677BEEC", 16),
    "cx": int("2F86FA60A081091A23DD795E1E3C689EE512A3C82EE0DCC2643C78EEA8FCACD35492558486B20F1C9EC197C90699850260C93BCBCD9C5C3317E19344E173AE36", 16),
    "cy": int("0EB488140F7E2F4E35CF220BDBC75AE44F26F9C7DF52E82436BDE80A91831DA27C8100DAA876F9ADC0D28A82DD3826D4DC7F92E471DA23E55E0EBB3927C85BD6", 16),
    "r": int("2F86FA60A081091A23DD795E1E3C689EE512A3C82EE0DCC2643C78EEA8FCACD35492558486B20F1C9EC197C90699850260C93BCBCD9C5C3317E19344E173AE36", 16),
    "s": int("1081B394696FFE8E6585E7A9362D26B6325F56778AADBC081C0BFBE933D52FF5823CE288E8C4F362526080DF7F70CE406A6EEB1F56919CB92A9853BDE73E5B4A", 16),
    "v": int("30D212A9E25D1A80A0F238532CADF3E64D7EF4E782B6AD140AAF8BBD9BB472984595EEC87B2F3448A1999D5F0A6DE0E14A55AD875721EC8CFD504000B3A840FF", 16),
    "z1": int("3D38E7262D69BB2AD24DD81EEA2F92E6348D619FA45007B175837CF13B026079051A48A1A379188F37BA46CE12F7207F2A8345459FF960E1EBD5B4F2A34A6EEF", 16),
    "z2": int("1A18A31602E6EAC0A9888C01941082AEFE296F840453D2603414C2A16EB6FC529D8D8372E50DC49D6C612CE1FF65BD58E1D2029F22690438CC36A76DDA444ACB", 16),
}

DEFAULT_CURVE = dict(STANDARD_CURVE)

CURRENT_CURVE = dict(DEFAULT_CURVE)


def curve_name(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return curve["name"]


def curve_p(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return curve["p"]


def curve_a(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return curve["a"]


def curve_b(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return curve["b"]


def curve_q(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return curve["q"]


def curve_g(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return (curve["gx"], curve["gy"])


def curve_key_size(curve=None):
    if curve is None:
        curve = CURRENT_CURVE
    return (curve["q"].bit_length() + 7) // 8


def set_current_curve(curve):
    global CURRENT_CURVE
    CURRENT_CURVE = dict(curve)



def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def add_mod_512(a, b):
    total = (int.from_bytes(a, "big") + int.from_bytes(b, "big")) % (1 << 512)
    return total.to_bytes(BLOCK_SIZE, "big")


def s_transform(data):
    return bytes(PI[byte] for byte in data)


def p_transform(data):
    return bytes(data[index] for index in TAU)


def l_transform(data):
    result = bytearray()
    for offset in range(0, BLOCK_SIZE, 8):
        block = data[offset:offset + 8]
        value = 0
        for byte_index, byte in enumerate(block):
            for bit_index in range(8):
                if byte & (1 << (7 - bit_index)):
                    value ^= A_MATRIX[byte_index * 8 + bit_index]
        result.extend(value.to_bytes(8, "big"))
    return bytes(result)


def lps_transform(data):
    return l_transform(p_transform(s_transform(data)))


def e_transform(key, message):
    state = message
    round_key = key
    for constant in C_CONSTANTS:
        state = lps_transform(xor_bytes(state, round_key))
        round_key = lps_transform(xor_bytes(round_key, constant))
    return xor_bytes(state, round_key)


def g_transform(n, h, message):
    key = lps_transform(xor_bytes(h, n))
    encrypted = e_transform(key, message)
    return xor_bytes(xor_bytes(encrypted, h), message)


def pad_message_block(block):
    return b"\x00" * (BLOCK_SIZE - len(block) - 1) + b"\x01" + block


def streebog_256(data):
    h = IV_256
    n = ZERO_512
    sigma = ZERO_512
    tail = data

    while len(tail) >= BLOCK_SIZE:
        block = tail[-BLOCK_SIZE:]
        tail = tail[:-BLOCK_SIZE]
        h = g_transform(n, h, block)
        n = add_mod_512(n, BLOCK_BITS)
        sigma = add_mod_512(sigma, block)

    block = pad_message_block(tail)
    h = g_transform(n, h, block)
    n = add_mod_512(n, (len(tail) * 8).to_bytes(BLOCK_SIZE, "big"))
    sigma = add_mod_512(sigma, block)
    h = g_transform(ZERO_512, h, n)
    h = g_transform(ZERO_512, h, sigma)
    return h[32:]


#арифметика эллиптической кривой
def euclid_algorithm(a, b):
    x2, x1 = 1, 0
    y2, y1 = 0, 1

    while b > 0:
        q = a // b
        r = a - q * b
        x = x2 - q * x1
        y = y2 - q * y1

        a, b = b, r
        x2, x1 = x1, x
        y2, y1 = y1, y

    return a, x2, y2


def mod_inverse(a, p):
    a = a % p
    if a == 0:
        raise ValueError("Обратный элемент не существует.")
    d, x, y = euclid_algorithm(a, p)
    if d != 1:
        raise ValueError("Обратный элемент не существует.")
    return x % p


def point_curve(point, curve=None):
    if point is INFINITY:
        return True
    p_mod = curve_p(curve)
    a_value = curve_a(curve)
    b_value = curve_b(curve)
    x, y = point
    left = (y * y) % p_mod
    right = (pow(x, 3, p_mod) + a_value * x + b_value) % p_mod
    return left == right


def point_negation(point, curve=None):
    if point is INFINITY:
        return INFINITY
    p_mod = curve_p(curve)
    x, y = point
    return (x, (-y) % p_mod)


def point_addition(point_p, point_q, curve=None):
    if point_p is INFINITY:
        return point_q
    if point_q is INFINITY:
        return point_p

    p_mod = curve_p(curve)
    a_value = curve_a(curve)
    x1, y1 = point_p
    x2, y2 = point_q

    if x1 == x2 and (y1 + y2) % p_mod == 0:
        return INFINITY

    if point_p == point_q:
        if y1 == 0:
            return INFINITY
        lam = ((3 * x1 * x1 + a_value) * mod_inverse(2 * y1, p_mod)) % p_mod
    else:
        lam = ((y2 - y1) * mod_inverse(x2 - x1, p_mod)) % p_mod

    x3 = (lam * lam - x1 - x2) % p_mod
    y3 = (lam * (x1 - x3) - y1) % p_mod
    return (x3, y3)


def scalar_multiply(point, k, curve=None):
    if point is INFINITY or k == 0:
        return INFINITY

    if k < 0:
        return scalar_multiply(point_negation(point, curve), -k, curve)

    result = INFINITY
    current = point

    while k > 0:
        if k & 1:
            result = point_addition(result, current, curve)
        current = point_addition(current, current, curve)
        k >>= 1

    return result


def generate_private_key(curve=None):
    return random.randint(1, curve_q(curve) - 1)


def derive_public_key(private_key, curve=None):
    public_key = scalar_multiply(curve_g(curve), private_key, curve)
    if public_key is INFINITY:
        raise ValueError("Не удалось получить открытый ключ.")
    return public_key


def digest_to_e(digest, curve=None):
    e = int.from_bytes(digest, "big") % curve_q(curve)
    if e == 0:
        e = 1
    return e


def sign_digest(digest, private_key, curve=None, k_value=None):
    q_value = curve_q(curve)
    e = digest_to_e(digest, curve)

    while True:
        # Для обычной работы k выбирается случайно.
        # Для контрольного примера из ГОСТ можно передать фиксированное k через k_value.
        if k_value is None:
            k = random.randint(1, q_value - 1)
        else:
            k = k_value

        point_c = scalar_multiply(curve_g(curve), k, curve)
        if point_c is INFINITY:
            if k_value is not None:
                raise ValueError("Для указанного k получена бесконечно удаленная точка.")
            continue

        r = point_c[0] % q_value
        if r == 0:
            if k_value is not None:
                raise ValueError("Для указанного k получилось r = 0.")
            continue

        s = (r * private_key + k * e) % q_value
        if s == 0:
            if k_value is not None:
                raise ValueError("Для указанного k получилось s = 0.")
            continue

        return r, s


def verify_digest(digest, signature, public_key, curve=None):
    q_value = curve_q(curve)
    r, s = signature
    if not (0 < r < q_value and 0 < s < q_value):
        return False

    if not point_curve(public_key, curve):
        return False

    if scalar_multiply(public_key, q_value, curve) is not INFINITY:
        return False

    e = digest_to_e(digest, curve)
    v = mod_inverse(e, q_value)
    z1 = (s * v) % q_value
    z2 = (-r * v) % q_value

    point_c = point_addition(
        scalar_multiply(curve_g(curve), z1, curve),
        scalar_multiply(public_key, z2, curve),
        curve,
    )

    if point_c is INFINITY:
        return False

    return point_c[0] % q_value == r


'''def hash_file(filename):
    with open(filename, "rb") as file:
        data = file.read()
    return streebog_256(data)'''

def hash_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = file.read().strip()
    return bytes.fromhex(data)


def to_hex(value, curve=None):
    return value.to_bytes(curve_key_size(curve), "big").hex()


def display_hex(value, curve=None):
    return to_hex(value, curve).upper()


def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        for key, value in data.items():
            file.write(f"{key}={value}\n")


def load_data(filename):
    data = {}
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def save_private_key(filename, private_key):
    save_data(
        filename,
        {
            "type": "private",
            "curve": curve_name(),
            "p": hex(curve_p())[2:],
            "a": hex(curve_a())[2:],
            "b": hex(curve_b())[2:],
            "q": hex(curve_q())[2:],
            "gx": hex(curve_g()[0])[2:],
            "gy": hex(curve_g()[1])[2:],
            "d": to_hex(private_key),
        },
    )


def save_public_key(filename, public_key):
    save_data(
        filename,
        {
            "type": "public",
            "curve": curve_name(),
            "p": hex(curve_p())[2:],
            "a": hex(curve_a())[2:],
            "b": hex(curve_b())[2:],
            "q": hex(curve_q())[2:],
            "gx": hex(curve_g()[0])[2:],
            "gy": hex(curve_g()[1])[2:],
            "x": to_hex(public_key[0]),
            "y": to_hex(public_key[1]),
        },
    )


def save_signature(filename, signature):
    save_data(
        filename,
        {
            "type": "signature",
            "curve": curve_name(),
            "p": hex(curve_p())[2:],
            "a": hex(curve_a())[2:],
            "b": hex(curve_b())[2:],
            "q": hex(curve_q())[2:],
            "gx": hex(curve_g()[0])[2:],
            "gy": hex(curve_g()[1])[2:],
            "hash": "gost3411-2012-256",
            "r": to_hex(signature[0]),
            "s": to_hex(signature[1]),
        },
    )


def build_curve_from_data(data):
    if "p" not in data or "a" not in data or "b" not in data or "q" not in data or "gx" not in data or "gy" not in data:
        raise ValueError("В файле не хватает параметров кривой.")
    return {
        "name": data.get("curve", data.get("name", "custom-curve")),
        "p": int(data["p"], 16),
        "a": int(data["a"], 16),
        "b": int(data["b"], 16),
        "q": int(data["q"], 16),
        "gx": int(data["gx"], 16),
        "gy": int(data["gy"], 16),
    }


def load_curve_file(filename):
    return build_curve_from_data(load_data(filename))


def load_private_key(filename):
    data = load_data(filename)
    curve = build_curve_from_data(data)
    private_key = int(data["d"], 16)
    if not (1 <= private_key < curve_q(curve)):
        raise ValueError("Некорректный закрытый ключ.")
    return curve, private_key


def load_public_key(filename):
    data = load_data(filename)
    curve = build_curve_from_data(data)
    public_key = (int(data["x"], 16), int(data["y"], 16))
    if not point_curve(public_key, curve):
        raise ValueError("Некорректный открытый ключ.")
    return curve, public_key


def load_signature(filename):
    data = load_data(filename)
    curve = build_curve_from_data(data)
    return curve, (int(data["r"], 16), int(data["s"], 16))


def input_path(prompt, default=""):
    while True:
        if default:
            path = input(f"{prompt} [{default}]: ").strip()
            if not path:
                path = default
        else:
            path = input(f"{prompt}: ").strip()

        if not path:
            print("Путь не может быть пустым.")
            continue
        return path


def print_header():
    print("\n" + "=" * 72)
    print("   ПРАКТИЧЕСКАЯ РАБОТА №4: ЭЛЕКТРОННАЯ ПОДПИСЬ")
    print("=" * 72)


def print_curve_parameters(curve):
    print("\nПараметры кривой:")
    print("name =", curve["name"])
    print("p    =", display_hex(curve["p"], curve))
    print("a    =", display_hex(curve["a"], curve))
    print("b    =", display_hex(curve["b"], curve))
    print("q    =", display_hex(curve["q"], curve))
    print("gx   =", display_hex(curve["gx"], curve))
    print("gy   =", display_hex(curve["gy"], curve))


def print_check(label, actual, expected, curve):
    print(f"\n{label}:")
    print("вычислено :", display_hex(actual, curve))
    print("ожидается :", display_hex(expected, curve))
    print("совпало   :", actual == expected)


def show_example_1_parameters():
    curve = GOST_EXAMPLE_1["curve"]
    print("\n" + GOST_EXAMPLE_1["name"])
    print_curve_parameters(curve)
    print("\nd =", display_hex(GOST_EXAMPLE_1["d"], curve))
    print("e =", display_hex(GOST_EXAMPLE_1["e"], curve))
    print("k =", display_hex(GOST_EXAMPLE_1["k"], curve))


def run_gost_example_1_sign():
    example = GOST_EXAMPLE_1
    curve = example["curve"]
    digest = example["e"].to_bytes(curve_key_size(curve), "big")

    public_key = derive_public_key(example["d"], curve)
    point_c = scalar_multiply(curve_g(curve), example["k"], curve)
    r_value, s_value = sign_digest(digest, example["d"], curve, k_value=example["k"])

    show_example_1_parameters()
    print_check("Qx", public_key[0], example["qx"], curve)
    print_check("Qy", public_key[1], example["qy"], curve)
    print_check("Cx", point_c[0], example["cx"], curve)
    print_check("Cy", point_c[1], example["cy"], curve)
    print_check("r", r_value, example["r"], curve)
    print_check("s", s_value, example["s"], curve)


def run_gost_example_1_verify():
    example = GOST_EXAMPLE_1
    curve = example["curve"]
    digest = example["e"].to_bytes(curve_key_size(curve), "big")
    public_key = (example["qx"], example["qy"])
    signature = (example["r"], example["s"])

    e_value = digest_to_e(digest, curve)
    v_value = mod_inverse(e_value, curve_q(curve))
    z1_value = (signature[1] * v_value) % curve_q(curve)
    z2_value = (-signature[0] * v_value) % curve_q(curve)
    point_c = point_addition(
        scalar_multiply(curve_g(curve), z1_value, curve),
        scalar_multiply(public_key, z2_value, curve),
        curve,
    )
    r_value = point_c[0] % curve_q(curve)
    is_valid = verify_digest(digest, signature, public_key, curve)

    show_example_1_parameters()
    print_check("v", v_value, example["v"], curve)
    print_check("z1", z1_value, example["z1"], curve)
    print_check("z2", z2_value, example["z2"], curve)
    print_check("Cx", point_c[0], example["cx"], curve)
    print_check("Cy", point_c[1], example["cy"], curve)
    print_check("R", r_value, example["r"], curve)
    print("\nПодпись прошла проверку:", is_valid)


def show_example_2_parameters():
    curve = GOST_EXAMPLE_2["curve"]
    print("\n" + GOST_EXAMPLE_2["name"])
    print_curve_parameters(curve)
    print("\nd =", display_hex(GOST_EXAMPLE_2["d"], curve))
    print("e =", display_hex(GOST_EXAMPLE_2["e"], curve))
    print("k =", display_hex(GOST_EXAMPLE_2["k"], curve))


def run_gost_example_2_sign():
    example = GOST_EXAMPLE_2
    curve = example["curve"]
    digest = example["e"].to_bytes(curve_key_size(curve), "big")

    public_key = derive_public_key(example["d"], curve)
    point_c = scalar_multiply(curve_g(curve), example["k"], curve)
    r_value, s_value = sign_digest(digest, example["d"], curve, k_value=example["k"])

    show_example_2_parameters()
    print_check("Qx", public_key[0], example["qx"], curve)
    print_check("Qy", public_key[1], example["qy"], curve)
    print_check("Cx", point_c[0], example["cx"], curve)
    print_check("Cy", point_c[1], example["cy"], curve)
    print_check("r", r_value, example["r"], curve)
    print_check("s", s_value, example["s"], curve)


def run_gost_example_2_verify():
    example = GOST_EXAMPLE_2
    curve = example["curve"]
    digest = example["e"].to_bytes(curve_key_size(curve), "big")
    public_key = (example["qx"], example["qy"])
    signature = (example["r"], example["s"])

    e_value = digest_to_e(digest, curve)
    v_value = mod_inverse(e_value, curve_q(curve))
    z1_value = (signature[1] * v_value) % curve_q(curve)
    z2_value = (-signature[0] * v_value) % curve_q(curve)
    point_c = point_addition(
        scalar_multiply(curve_g(curve), z1_value, curve),
        scalar_multiply(public_key, z2_value, curve),
        curve,
    )
    r_value = point_c[0] % curve_q(curve)
    is_valid = verify_digest(digest, signature, public_key, curve)

    show_example_2_parameters()
    print_check("v", v_value, example["v"], curve)
    print_check("z1", z1_value, example["z1"], curve)
    print_check("z2", z2_value, example["z2"], curve)
    print_check("Cx", point_c[0], example["cx"], curve)
    print_check("Cy", point_c[1], example["cy"], curve)
    print_check("R", r_value, example["r"], curve)
    print("\nПодпись прошла проверку:", is_valid)


def example_1_menu():
    while True:
        print("\nПример 1 из ГОСТ:")
        print("1. Показать входные параметры")
        print("2. Проверить формирование открытого ключа и подписи")
        print("3. Проверить проверку подписи")
        print("4. Назад")

        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                show_example_1_parameters()
            elif choice == "2":
                run_gost_example_1_sign()
            elif choice == "3":
                run_gost_example_1_verify()
            elif choice == "4":
                break
            else:
                print("Неверный пункт меню.")
        except Exception as error:
            print("\nОшибка:", error)


def example_2_menu():
    while True:
        print("\nПример 2 из ГОСТ:")
        print("1. Показать входные параметры")
        print("2. Проверить формирование открытого ключа и подписи")
        print("3. Проверить проверку подписи")
        print("4. Назад")

        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                show_example_2_parameters()
            elif choice == "2":
                run_gost_example_2_sign()
            elif choice == "3":
                run_gost_example_2_verify()
            elif choice == "4":
                break
            else:
                print("Неверный пункт меню.")
        except Exception as error:
            print("\nОшибка:", error)


def generate_keypair_flow():
    set_current_curve(DEFAULT_CURVE)
    private_key_file = input_path("Файл для закрытого ключа", "private_key.txt")
    public_key_file = input_path("Файл для открытого ключа", "public_key.txt")

    private_key = generate_private_key()
    public_key = derive_public_key(private_key)

    save_private_key(private_key_file, private_key)
    save_public_key(public_key_file, public_key)

    print("\nКлючевая пара создана.")
    print("Закрытый ключ сохранен в:", private_key_file)
    print("Открытый ключ сохранен в:", public_key_file)


def sign_file_flow():
    message_file = input_path("Файл для подписи")
    private_key_file = input_path("Файл с закрытым ключом", "private_key.txt")
    signature_file = input_path("Файл для сохранения подписи", "signature.txt")

    if not os.path.exists(message_file):
        raise FileNotFoundError("Файл для подписи не найден.")
    if not os.path.exists(private_key_file):
        raise FileNotFoundError("Файл закрытого ключа не найден.")

    curve, private_key = load_private_key(private_key_file)
    digest = hash_file(message_file)
    signature = sign_digest(digest, private_key, curve)

    set_current_curve(curve)
    save_signature(signature_file, signature)

    print("\nПодпись сформирована.")
    print("Хэш файла:", digest.hex())
    print("Подпись сохранена в:", signature_file)


def verify_file_flow():
    message_file = input_path("Файл для проверки")
    signature_file = input_path("Файл с подписью", "signature.txt")
    public_key_file = input_path("Файл с открытым ключом", "public_key.txt")

    if not os.path.exists(message_file):
        raise FileNotFoundError("Файл для проверки не найден.")
    if not os.path.exists(signature_file):
        raise FileNotFoundError("Файл подписи не найден.")
    if not os.path.exists(public_key_file):
        raise FileNotFoundError("Файл открытого ключа не найден.")

    digest = hash_file(message_file)
    signature_curve, signature = load_signature(signature_file)
    public_curve, public_key = load_public_key(public_key_file)

    if signature_curve != public_curve:
        raise ValueError("Подпись и открытый ключ относятся к разным параметрам кривой.")

    is_valid = verify_digest(digest, signature, public_key, public_curve)

    print("\nРезультат проверки:")
    print("Хэш файла:", digest.hex())
    if is_valid:
        print("Подпись верна.")
    else:
        print("Подпись неверна.")


def standard_menu():
    set_current_curve(DEFAULT_CURVE)
    while True:
        print("\nСтандартные параметры ГОСТ:")
        print("1. Показать параметры кривой")
        print("2. Сгенерировать ключевую пару")
        print("3. Подписать файл")
        print("4. Проверить подпись")
        print("5. Назад")

        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                print_curve_parameters(DEFAULT_CURVE)
            elif choice == "2":
                generate_keypair_flow()
            elif choice == "3":
                sign_file_flow()
            elif choice == "4":
                verify_file_flow()
            elif choice == "5":
                break
            else:
                print("Неверный пункт меню.")
        except Exception as error:
            print("\nОшибка:", error)


def gost_examples_menu():
    while True:
        print("\nПроверка примеров из ГОСТ:")
        print("1. Пример 1")
        print("2. Пример 2")
        print("3. Назад")

        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                example_1_menu()
            elif choice == "2":
                example_2_menu()
            elif choice == "3":
                break
            else:
                print("Неверный пункт меню.")
        except Exception as error:
            print("\nОшибка:", error)


def menu():
    while True:
        print("\nВыберите действие:")
        print("1. Алгоритм электронной подписи со стандартными параметрами ГОСТ")
        print("2. Алгоритм электронной подписи для проверки примеров из ГОСТ")
        print("3. Выход")

        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                standard_menu()
            elif choice == "2":
                gost_examples_menu()
            elif choice == "3":
                print("Завершение программы.")
                break
            else:
                print("Неверный пункт меню.")
        except Exception as error:
            print("\nОшибка:", error)


def main():
    print_header()
    menu()


if __name__ == "__main__":
    main()
