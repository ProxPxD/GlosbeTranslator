from parameterized import parameterized

from src.translating.argumentParsing.translatorCli import CURRENT_MODES_COL
from tests.abstractCliTest import AbstractCliTest


class MisplacedTest(AbstractCliTest):

    @classmethod
    def _get_test_name(cls) -> str:
        return 'Misplaced'

    @parameterized.expand([
        ('single_once', ['suchen'], ['de'], ['pl'], 't de suchen pl', '-s'),
        ('single_twice', ['suchen'], ['de'], ['pl'], 't de pl suchen', '-s'),
        ('single_no_from_lang', ['suchen'], ['de'], ['pl'], 't pl suchen', '-s'),
        ('lang_misplaced_before', ['suchen'], ['de'], ['pl', 'fr'], 't de suchen -m pl fr', None),
        ('lang_misplaced_after', ['suchen'], ['de'], ['pl', 'fr'], 't -m pl suchen fr', None),
        ('word_misplaced_one_word', ['suchen', 'nehmen', 'krank', 'Weib'], ['de'], ['pl'], 't pl suchen -w nehmen krank Weib', None),
        ('word_misplaced_two_words', ['suchen', 'nehmen', 'krank', 'Weib'], ['de'], ['pl'], 't suchen nehmen -w krank Weib', None),
    ])
    def test_misplaced(self, name: str, e_words: str, e_from_langs: str, e_to_langs: str, input_line: str, mode: str):
        words, from_langs, to_langs = self.cli.root.get_collections('words', 'from_langs', 'to_langs')
        from_langs.set_default(e_from_langs)
        to_langs.set_default(e_to_langs)
        if mode:
            self.cli.root.get_collection(CURRENT_MODES_COL).set_default(mode)

        self.cli.parse_without_actions(input_line)

        self.assertCountEqual(e_words, words.get_plain())
        self.assertCountEqual(e_from_langs, from_langs.get_plain())
        self.assertCountEqual(e_to_langs, to_langs.get_plain())
