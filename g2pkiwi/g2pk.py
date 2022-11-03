import re

from jamo import h2j

from g2pkiwi.english import convert_eng
from g2pkiwi.idioms import idioms
from g2pkiwi.numerals import convert_num
from g2pkiwi.regular import link_all
from g2pkiwi.special import special_all
from g2pkiwi.utils import annotate, compose, get_rule_id2text, gloss, group, parse_table


class G2p:
    def __init__(self):
        self.table = parse_table()

        self.rule2text = get_rule_id2text()  # for comments of main rules

    def __call__(
        self,
        string: str,
        descriptive: bool = False,
        verbose: bool = False,
        group_vowels: bool = False,
        to_syl: bool = True,
    ) -> str:
        """Main function
        string: input string
        descriptive: boolean.
        verbose: boolean
        group_vowels: boolean.
            If True, the vowels of the identical sound are normalized.
        to_syl: boolean.
            If True, hangul letters or jamo are assembled to form syllables.

        For example, given an input string "나의 친구가 mp3 file 3개를 다운받고 있다",
        STEP 1. idioms
        -> 나의 친구가 엠피쓰리 file 3개를 다운받고 있다

        STEP 2. English to Hangul
        -> 나의 친구가 엠피쓰리 파일 3개를 다운받고 있다

        STEP 3. annotate
        -> 나의/J 친구가 엠피쓰리 파일 3개/B를 다운받고 있다

        STEP 4. Spell out arabic numbers
        -> 나의/J 친구가 엠피쓰리 파일 세개/B를 다운받고 있다

        STEP 5. decompose
        -> 나의/J 친구가 엠피쓰리 파일 세개/B를 다운받고 있다

        STEP 6-9. Hangul
        -> 나의 친구가 엠피쓰리 파일 세개를 다운받꼬 읻따
        """
        # 1. idioms
        string = idioms(string, descriptive, verbose)

        # 2 English to Hangul
        string = convert_eng(string)

        # 3. annotate
        string = annotate(string)

        # 4. Spell out arabic numbers
        string = convert_num(string)

        # 5. decompose
        inp = h2j(string)

        # 6. special
        inp = special_all(inp, descriptive, verbose)
        inp = re.sub(r"/[PJEB]", "", inp)

        # 7. regular table: batchim + onset
        for str1, str2, rule_ids in self.table:
            _inp = inp
            inp = re.sub(str1, str2, inp)

            if len(rule_ids) > 0:
                rule = "\n".join(
                    self.rule2text.get(rule_id, "") for rule_id in rule_ids
                )
            else:
                rule = ""
            gloss(verbose, inp, _inp, rule)

        # 8 link
        inp = link_all(inp, descriptive, verbose)

        # 9. postprocessing
        if group_vowels:
            inp = group(inp)

        if to_syl:
            inp = compose(inp)

        inp = inp.replace("‖", "")
        return inp


if __name__ == "__main__":
    g2p = G2p()
    g2p("나의 친구가 mp3 file 3개를 다운받고 있다")
