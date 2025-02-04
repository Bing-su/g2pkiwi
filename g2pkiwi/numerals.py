"""
https://github.com/kyubyong/g2pK
"""
import re

# This is a list of bound nouns preceded by pure Korean numerals.
BOUND_NOUNS = (
    "군데 권 개 그루 닢 대 두 마리 명 모 모금 뭇 발 발짝 방 번 벌 보루 살 수 술 시 시간 쌈 움큼 정 짝 채 척 첩 축 켤레 톨 통"
)
BOUND_NOUNS = BOUND_NOUNS.split()

digits = "123456789"
names = "일이삼사오육칠팔구"
digit2name = {d: n for d, n in zip(digits, names)}

modifiers = "한 두 세 네 다섯 여섯 일곱 여덟 아홉"
decimals = "열 스물 서른 마흔 쉰 예순 일흔 여든 아흔"
digit2mod = {d: mod for d, mod in zip(digits, modifiers.split())}
digit2dec = {d: dec for d, dec in zip(digits, decimals.split())}


def process_num(num: str, sino: bool = True) -> str:
    """Process a string looking like arabic number.
    num: string. Consists of [0-9,]. e.g., 12,345
    sino: boolean. If True, sino-Korean numerals, i.e., 일, 이, .. are considered.
        Otherwise, pure Korean ones in their modifying forms
                   such as 한, 두, ... are returned.

    >>> process_num("123,456,789", sino=True)
    일억이천삼백사십오만육천칠백팔십구

    >>> process_num("123,456,789", sino=False)
    일억이천삼백사십오만육천칠백여든아홉
    """
    num = num.replace(",", "")

    if num == "0":
        return "영"
    if not sino and num == "20":
        return "스무"

    spelledout = []
    for i, digit in enumerate(num):
        i = len(num) - i - 1
        name = None
        if sino:
            if i == 0:
                name = digit2name.get(digit, "")
            elif i == 1:
                name = digit2name.get(digit, "") + "십"
                name = name.replace("일십", "십")
        else:
            if i == 0:
                name = digit2mod.get(digit, "")
            elif i == 1:
                name = digit2dec.get(digit, "")

        if digit == "0":
            if i % 4 == 0:
                last_three = spelledout[-min(3, len(spelledout)) :]
                if "".join(last_three) == "":
                    spelledout.append("")
                    continue
            else:
                spelledout.append("")
                continue
        if i == 2:
            name = digit2name.get(digit, "") + "백"
            name = name.replace("일백", "백")
        elif i == 3:
            name = digit2name.get(digit, "") + "천"
            name = name.replace("일천", "천")
        elif i == 4:
            name = digit2name.get(digit, "") + "만"
            name = name.replace("일만", "만")
        elif i == 5:
            name = digit2name.get(digit, "") + "십"
            name = name.replace("일십", "십")
        elif i == 6:
            name = digit2name.get(digit, "") + "백"
            name = name.replace("일백", "백")
        elif i == 7:
            name = digit2name.get(digit, "") + "천"
            name = name.replace("일천", "천")
        elif i == 8:
            name = digit2name.get(digit, "") + "억"
        elif i == 9:
            name = digit2name.get(digit, "") + "십"
        elif i == 10:
            name = digit2name.get(digit, "") + "백"
        elif i == 11:
            name = digit2name.get(digit, "") + "천"
        elif i == 12:
            name = digit2name.get(digit, "") + "조"
        elif i == 13:
            name = digit2name.get(digit, "") + "십"
        elif i == 14:
            name = digit2name.get(digit, "") + "백"
        elif i == 15:
            name = digit2name.get(digit, "") + "천"
        elif i == 16:
            name = digit2name.get(digit, "") + "경"
        elif i == 17:
            name = digit2name.get(digit, "") + "십"
        elif i == 18:
            name = digit2name.get(digit, "") + "백"
        elif i == 19:
            name = digit2name.get(digit, "") + "천"

        if name is not None:
            spelledout.append(name)
        else:
            # too long digit
            return num

    return "".join(elem for elem in spelledout)


def convert_num(string):
    """Convert a annotated string such that arabic numerals inside are spelled out.
    >>> convert_num("우리 3시/B 10분/B에 만나자.")
    우리 세시/B 십분/B에 만나자.
    """
    global BOUND_NOUNS

    # Bound Nouns
    tokens = set(re.findall(r"(\d[\d,]*\d|\d)(\s*[ㄱ-힣]+(?=/B))", string))
    tokens = sorted(tokens, key=len, reverse=True)
    for token in tokens:
        num, bn = token
        bn_s = bn.lstrip()
        if bn_s in BOUND_NOUNS:
            spelledout = process_num(num, sino=False)
        else:
            spelledout = process_num(num, sino=True)

        string = string.replace(f"{num}{bn}/B", f"{spelledout}{bn}/B")

    # remain digits
    remain = set(re.findall(r"(\d[\d,]*\d|\d)", string))
    remain = sorted(remain, key=len, reverse=True)
    for num in remain:
        string = string.replace(num, process_num(num, sino=True))

    # digit by digit for still remaining digits
    digits = "0123456789"
    names = "영일이삼사오육칠팔구"
    for d, n in zip(digits, names):
        string = string.replace(d, n)

    # special cases
    pairs = [("십육", "심뉵"), ("백육", "뱅뉵")]

    for str1, str2 in pairs:
        string = string.replace(str1, str2)

    return string


if __name__ == "__main__":
    # test
    print(process_num("123,456,789", sino=True))
    print(process_num("123,456,789", sino=False))
    print(convert_num("우리 3시/B 10분/B에 만나자."))
