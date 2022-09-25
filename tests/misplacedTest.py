from src.translating.configs.configurations import Configurations
from tests.abstractTranslationTest import AbstractTranslationTest


class MisplacedTest(AbstractTranslationTest):
    def _perform_translation(self):  # TODO: create another class to handle the translation and to be used both in src and tests
       return None

    @classmethod
    def _get_mode(cls) -> str | None:
        return None

    @classmethod
    def _get_test_name(cls) -> str:
        return 'misplaced'

    def test_single_misplaced_once(self):
        word, from_lang, to_lang = 'suchen', 'de', 'pl'
        self.set_input_string(f't {from_lang} {word} {to_lang} -s')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertIn(to_lang, self.argumentParser.to_langs)
        self.assertEqual({word}, set(self.argumentParser.words))

    def test_single_misplaced_twice(self):
        word, from_lang, to_lang = 'suchen', 'de', 'pl'
        self.set_input_string(f't {from_lang} {to_lang} {word} -s')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertIn(to_lang, self.argumentParser.to_langs)
        self.assertEqual({word}, set(self.argumentParser.words))

    def test_single_misplaced_one_arg(self):
        word, from_lang, to_lang = 'suchen', 'de', 'pl'
        Configurations.change_last_used_languages(from_lang)
        self.set_input_string(f't {to_lang} {word} -s')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertIn(to_lang, self.argumentParser.to_langs)
        self.assertEqual({word}, set(self.argumentParser.words))

    def test_multi_langs_misplaced_before(self):
        word, from_lang, to_langs = 'suchen', 'de', ['pl', 'fr']
        self.set_input_string(f't {from_lang} {word} -m {" ".join(to_langs)}')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertEqual(to_langs, self.argumentParser.to_langs)
        self.assertEqual({word}, set(self.argumentParser.words))

    def test_multi_langs_misplaced_after(self):
        word, from_lang, to_langs = 'suchen', 'de', ['pl', 'fr']
        Configurations.change_last_used_languages(from_lang)
        self.set_input_string(f't -m {word} {" ".join(to_langs)}')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertEqual(to_langs, self.argumentParser.to_langs)
        self.assertEqual({word}, set(self.argumentParser.words))

    def test_multi_word_misplaced_one_word(self):
        words, from_lang, to_lang = ['suchen', 'nehmen', 'krank', 'Weib'], 'de', 'pl'
        words_1, words_2 = words[:2], words[2:]
        Configurations.change_last_used_languages(from_lang)
        self.set_input_string(f't {to_lang} {" ".join(words_1)} -w {" ".join(words_2)}')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertIn(to_lang, self.argumentParser.to_langs)
        self.assertEqual(set(words), set(self.argumentParser.words))

    def test_multi_word_misplaced_two_words(self):
        words, from_lang, to_lang = ['suchen', 'nehmen', 'krank', 'Weib'], 'de', 'pl'
        words_1, words_2 = words[:2], words[2:]
        Configurations.change_last_used_languages(from_lang, to_lang)
        self.set_input_string(f't {" ".join(words_1)} -w {" ".join(words_2)}')

        self.argumentParser.parse()

        self.assertEqual(from_lang, self.argumentParser.from_lang)
        self.assertIn(to_lang, self.argumentParser.to_langs)
        self.assertEqual(set(words), set(self.argumentParser.words))