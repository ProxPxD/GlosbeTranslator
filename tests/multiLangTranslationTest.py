from src.translating.argumentParsing.abstractParsing.src import FLAGS
from src.translating.argumentParsing.abstractParsing.src.parsingException import ParsingException
from src.translating.configs.configurations import Configurations, Configs
from tests.abstractTranslationTest import AbstractTranslationTest


class MultiLangTranslationTest(AbstractTranslationTest):

    @classmethod
    def _get_mode(cls):
        return FLAGS.MULTI_LANG

    @classmethod
    def _get_test_name(cls) -> str:
        return cls._get_mode() + ' mode'

    def _perform_translation(self):
        word = self.argumentParser.words[0] if self.argumentParser.words else None
        from_lang = self.argumentParser.from_lang
        to_langs = self.argumentParser.to_langs
        return self.translator.multi_lang_translate(word, to_langs, from_lang)

    def test_all_args_set(self):
        word, from_lang = 'Schweiz', 'de'
        to_langs = ['pl', 'es', 'zh']
        self.set_input_string(f't {word} {from_lang} {" ".join(to_langs)}')

        translations = self.translate()

        correct_translated_words = ['Szwajcaria', 'Suiza', '瑞士']
        self.assertEqual(len(translations), len(to_langs))
        for i, lang in enumerate(to_langs):
            translation = translations[i]
            batch = self.get_nth_translation_batch(0, translation)
            translation_word = self.get_word_from_batch(batch)
            self.assertEqual(lang, self.get_constant_part(translation))
            self.assertEqual(translation_word, correct_translated_words[i])

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

    def test_only_langs_set(self):
        from_lang = 'zh'
        to_langs = ['pl', 'es', 'de']
        Configurations.change_last_used_languages(from_lang)
        self.set_input_string(f't -m {" ".join(to_langs)}')

        self.assertRaises(ParsingException, self.translate)
        self.assertFalse(self.argumentParser.is_translation_mode_on())

    def test_only_word_set(self):
        word, from_lang = '女人', 'zh'
        to_langs = ['pl', 'es', 'de']
        Configurations.change_conf(Configs.LANG_LIMIT, len(to_langs))
        Configurations.change_last_used_languages(from_lang, *to_langs)
        self.set_input_string(f't {word} -m')

        translations = self.translate()

        correct_translated_words = ['kobieta', 'mujer', 'Frau']
        self.assertEqual(len(translations), len(to_langs))
        self.assertEqual(from_lang, self.argumentParser.from_lang)
        for i, lang in enumerate(to_langs):
            translation = translations[i]
            batch = self.get_nth_translation_batch(0, translation)
            translation_word = self.get_word_from_batch(batch)
            self.assertEqual(lang, self.get_constant_part(translation))
            self.assertEqual(translation_word, correct_translated_words[i])
