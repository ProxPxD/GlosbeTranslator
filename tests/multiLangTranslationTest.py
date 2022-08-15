from src.translating.argumentParsing.configurations import Configurations
from src.translating.argumentParsing.constants import FullModes
from tests.abstractTranslationTest import AbstractTranslationTest


class MultiLangTranslationTest(AbstractTranslationTest):

    @classmethod
    def _get_mode(cls):
        return FullModes.MULTI_LANG

    def _perform_translation(self):
        word = self.argumentParser.words[0]
        from_lang = self.argumentParser.from_lang
        to_langs = self.argumentParser.to_langs
        return self.translator.multi_lang_translate(word, to_langs, from_lang)

    def test_all_args_set(self):
        word, from_lang = 'Schweiz', 'de'
        to_langs = ['pl', 'es', 'zh']
        self.set_input_string(f't {word} {from_lang} {" ".join(to_langs)}')

        translations = self.translate()

        self.assertEqual(len(translations), 3)
        for i, lang in enumerate(to_langs):
            self.assertEqual(lang, self.get_constant_part(translations[i]))

    def test_no_from_language_arg_set(self):
        word, from_lang = '女人', 'zh'
        to_langs = ['pl', 'es', 'de']
        Configurations.change_last_used_languages(from_lang)
        self.set_input_string(f't {word} -m {" ".join(to_langs)}')

        translations = self.translate()

        correct_translated_words = ['kobieta', 'mujer', 'Frau']
        self.assertEqual(len(translations), len(to_langs))
        for i, lang in enumerate(to_langs):
            translation = translations[i]
            batch = self.get_nth_translation_batch(0, translation)
            translation_word = self.get_word_from_batch(batch)
            self.assertEqual(lang, self.get_constant_part(translation))
            self.assertEqual(translation_word, correct_translated_words[i])