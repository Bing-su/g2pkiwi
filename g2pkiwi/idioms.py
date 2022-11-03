import re
from pathlib import Path

from g2pkiwi.utils import gloss

idioms_file = Path(__file__).parent / "idioms.txt"
idioms_dict = {}
with idioms_file.open(encoding="utf-8") as file:
    for line in file:
        line = line.split("#")[0].strip()
        if "===" in line:
            str1, str2 = line.split("===")
            idioms_dict[str1] = str2

idioms_keys = sorted(idioms_dict.keys(), key=len, reverse=True)
pattern = re.compile("|".join(idioms_dict.keys()))


def idioms(inp: str, descriptive: bool = False, verbose: bool = False) -> str:
    "replace idioms"
    out = pattern.sub(lambda x: idioms_dict[x.group()], inp)
    gloss(verbose, out, inp, "from idioms.txt")
    return out
