from __future__ import annotations

import re
from pathlib import Path
from unicodedata import normalize

from jamo import j2h
from kiwipiepy import Kiwi

kiwi = Kiwi(model_type="sbg")


############## English ##############
def adjust(arpabets: list[str]) -> list[str]:
    """Modify arpabets so that it fits our processes"""
    string = " " + " ".join(arpabets) + " $"
    string = re.sub(r"\d", "", string)
    string = string.replace(" T S ", " TS ")
    string = string.replace(" D Z ", " DZ ")
    string = string.replace(" AW ER ", " AWER ")
    string = string.replace(" IH R $", " IH ER ")
    string = string.replace(" EH R $", " EH ER ")
    string = string.replace(" $", "")

    return string.strip("$ ").split()


def to_choseong(arpabet: str) -> str:
    """Arpabet to choseong or onset"""
    d = {
        "B": "ᄇ",
        "CH": "ᄎ",
        "D": "ᄃ",
        "DH": "ᄃ",
        "DZ": "ᄌ",
        "F": "ᄑ",
        "G": "ᄀ",
        "HH": "ᄒ",
        "JH": "ᄌ",
        "K": "ᄏ",
        "L": "ᄅ",
        "M": "ᄆ",
        "N": "ᄂ",
        "NG": "ᄋ",
        "P": "ᄑ",
        "R": "ᄅ",
        "S": "ᄉ",
        "SH": "ᄉ",
        "T": "ᄐ",
        "TH": "ᄉ",
        "TS": "ᄎ",
        "V": "ᄇ",
        "W": "W",
        "Y": "Y",
        "Z": "ᄌ",
        "ZH": "ᄌ",
    }

    return d.get(arpabet, arpabet)


def to_jungseong(arpabet: str) -> str:
    """Arpabet to jungseong or vowel"""
    d = {
        "AA": "ᅡ",
        "AE": "ᅢ",
        "AH": "ᅥ",
        "AO": "ᅩ",
        "AW": "ᅡ우",
        "AWER": "ᅡ워",
        "AY": "ᅡ이",
        "EH": "ᅦ",
        "ER": "ᅥ",
        "EY": "ᅦ이",
        "IH": "ᅵ",
        "IY": "ᅵ",
        "OW": "ᅩ",
        "OY": "ᅩ이",
        "UH": "ᅮ",
        "UW": "ᅮ",
    }
    return d.get(arpabet, arpabet)


def to_jongseong(arpabet: str) -> str:
    """Arpabet to jongseong or coda"""
    d = {
        "B": "ᆸ",
        "CH": "ᆾ",
        "D": "ᆮ",
        "DH": "ᆮ",
        "F": "ᇁ",
        "G": "ᆨ",
        "HH": "ᇂ",
        "JH": "ᆽ",
        "K": "ᆨ",
        "L": "ᆯ",
        "M": "ᆷ",
        "N": "ᆫ",
        "NG": "ᆼ",
        "P": "ᆸ",
        "R": "ᆯ",
        "S": "ᆺ",
        "SH": "ᆺ",
        "T": "ᆺ",
        "TH": "ᆺ",
        "V": "ᆸ",
        "W": "ᆼ",
        "Y": "ᆼ",
        "Z": "ᆽ",
        "ZH": "ᆽ",
    }

    return d.get(arpabet, arpabet)


def reconstruct(string: str) -> str:
    """Some postprocessing rules"""
    pairs = [
        ("그W", "ᄀW"),
        ("흐W", "ᄒW"),
        ("크W", "ᄏW"),
        ("ᄂYᅥ", "니어"),
        ("ᄃYᅥ", "디어"),
        ("ᄅYᅥ", "리어"),
        ("Yᅵ", "ᅵ"),
        ("Yᅡ", "ᅣ"),
        ("Yᅢ", "ᅤ"),
        ("Yᅥ", "ᅧ"),
        ("Yᅦ", "ᅨ"),
        ("Yᅩ", "ᅭ"),
        ("Yᅮ", "ᅲ"),
        ("Wᅡ", "ᅪ"),
        ("Wᅢ", "ᅫ"),
        ("Wᅥ", "ᅯ"),
        ("Wᅩ", "ᅯ"),
        ("Wᅮ", "ᅮ"),
        ("Wᅦ", "ᅰ"),
        ("Wᅵ", "ᅱ"),
        ("ᅳᅵ", "ᅴ"),
        ("Y", "ᅵ"),
        ("W", "ᅮ"),
    ]
    for str1, str2 in pairs:
        string = string.replace(str1, str2)
    return string


############## Hangul ##############
def parse_table():
    """Parse the main rule table"""
    table_path = Path(__file__).parent / "table.csv"
    lines = table_path.read_text("utf-8").splitlines()
    onsets = lines[0].split(",")
    table = []
    for line in lines[1:]:
        cols = line.split(",")
        coda = cols[0]
        for i, onset in enumerate(onsets):
            cell = cols[i]
            if len(cell) == 0:
                continue
            if i == 0:
                continue
            else:
                str1 = f"{coda}{onset}"
                if "(" in cell:
                    str2 = cell.split("(")[0]
                    rule_ids = cell.split("(")[1][:-1].split("/")
                else:
                    str2 = cell
                    rule_ids = []

                table.append((str1, str2, rule_ids))
    return table


############## Preprocessing ##############
def annotate(string: str) -> str:
    """attach pos tags to the given string using Mecab
    mecab: mecab object
    """
    norm = normalize("NFD", string)
    tokens = kiwi.tokenize(string)
    replace = []

    idx = 0
    for token in tokens:
        form, tag = token.form, token.tag
        dec = normalize("NFD", form)
        if form == "의" and tag[0] == "J":
            replace.append((dec, dec + "/J", idx))
        elif tag[0] == "E" and dec[-1] == "ᆯ":
            replace.append((dec, dec + "/E", idx))
        elif tag[0] == "V" and dec[-1] in "ᆫᆬᆷᆱᆰᆲᆴ":
            replace.append((dec, dec + "/P", idx))
        elif tag == "NNB":
            replace.append((dec, dec + "/B", idx))
        idx += len(dec)

    acc = 0
    for orig, repl, idx in replace:
        nxt = norm[: idx + acc] + norm[idx + acc :].replace(orig, repl, 1)
        if norm != nxt:
            acc += 2
        norm = nxt

    result = normalize("NFC", norm)

    return result


############## Postprocessing ##############
def compose(letters: str) -> str:
    # insert placeholder
    letters = re.sub(r"(^|[^\u1100-\u1112])([\u1161-\u1175])", r"\1ᄋ\2", letters)

    string = letters  # assembled characters
    # c+v+c
    syls = set(re.findall(r"[\u1100-\u1112][\u1161-\u1175][\u11A8-\u11C2]", string))
    for syl in syls:
        string = string.replace(syl, j2h(*syl))

    # c+v
    syls = set(re.findall(r"[\u1100-\u1112][\u1161-\u1175]", string))
    for syl in syls:
        string = string.replace(syl, j2h(*syl))

    return string


def group(inp: str) -> str:
    """For group_vowels=True
    Contemporarily, Korean speakers don't distinguish some vowels.
    """
    inp = inp.replace("ᅢ", "ᅦ")
    inp = inp.replace("ᅤ", "ᅨ")
    inp = inp.replace("ᅫ", "ᅬ")
    inp = inp.replace("ᅰ", "ᅬ")

    return inp


def _get_examples() -> list[str]:
    """For internal use"""
    rules_path = Path(__file__).parent / "rules.txt"
    text = rules_path.read_text(encoding="utf-8").splitlines()
    examples = []
    for line in text:
        if line.startswith("->"):
            examples.extend(re.findall(r"([ㄱ-힣][ ㄱ-힣]*)\[([ㄱ-힣][ ㄱ-힣]*)\]", line))
    _examples = []
    for inp, gt in examples:
        for each in gt.split("/"):
            _examples.append((inp, each))

    return _examples


############## Utilities ##############
def get_rule_id2text() -> dict[str, str]:
    """for verbose=True"""
    rules_path = Path(__file__).parent / "rules.txt"
    rules = rules_path.read_text("utf-8").strip().split("\n\n")

    rule_id2text: dict[str, str] = {}
    for rule in rules:
        rule_id, texts = rule.split("\n", maxsplit=1)
        rule_id2text[rule_id.strip()] = texts.strip()
    return rule_id2text


def gloss(verbose: bool, out: str, inp: str, rule: str):
    """displays the process and relevant information"""
    if verbose and out != inp and out != re.sub(r"/[EJPB]", "", inp):
        print(compose(inp), "->", compose(out))
        print("\033[1;31m", rule, "\033[0m")
