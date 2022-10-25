import csv
import unittest
from pathlib import Path

from g2pkiwi import G2p


g2p = G2p()


class G2pKiwiTest(unittest.TestCase):
    @staticmethod
    def str2bool(s: str) -> bool:
        return s in ("True", "true", "1", "yes")

    def compare(self, file_path: Path):
        with file_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, restval="")

            for row in reader:
                origin = row["origin"]
                convert = row["convert"]
                descriptive = self.str2bool(row["descriptive"])
                group_vowels = self.str2bool(row["group_vowels"])

                result = g2p(origin, descriptive=descriptive, group_vowels=group_vowels)
                with self.subTest(origin=origin, convert=result, expect=convert):
                    self.assertEqual(result, convert)

    def test_g2pk(self):
        # g2pk 패키지로 생성한 테스트 케이스
        path = Path(__file__).parent / "case_g2pk.csv"
        self.compare(path)

    def test_g2pkiwi(self):
        # g2pk와 동작이 다른 테스트 케이스
        path = Path(__file__).parent / "case_g2pkiwi.csv"
        self.compare(path)


if __name__ == "__main__":
    unittest.main()
