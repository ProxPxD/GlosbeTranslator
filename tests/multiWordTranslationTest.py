from src.translating.argumentParsing.IntelligentParser.src import FLAGS
from src.translating.configs.configurations import Configurations
from tests.abstractTranslationTest import AbstractTranslationTest


class MultiWordTranslationTest(AbstractTranslationTest):
    @classmethod
    def _perform_translation(self):
        words = self.argumentParser.words
        from_lang = self.argumentParser.from_lang
        to_lang = self.argumentParser.to_langs[0]
        return self.translator.multi_word_translate(to_lang, words, from_lang)

    @classmethod
    def _get_mode(cls) -> str:
        return FLAGS.MULTI_WORD

    @classmethod
    def _get_test_name(cls) -> str:
        return cls._get_mode() + ' mode'

    def test_all_args_set(self):
        from_lang, to_lang = 'pl', 'de'
        words = ['myśleć', 'ulec', 'obraz']
        self.set_input_string(f't {from_lang} {to_lang} {" ".join(words)}')

        translations = self.translate()

        correct_translated_words = ['denken', 'erliegen', 'Bild']
        self.assertEqual(len(translations), len(words))
        for i, word in enumerate(words):
            translation = translations[i]
            batch = self.get_nth_translation_batch(0, translation)
            translation_word = self.get_word_from_batch(batch)
            self.assertEqual(word, self.get_constant_part(translation))
            self.assertEqual(translation_word, correct_translated_words[i])

    def test_no_from_language_arg_set(self):
        from_lang, to_lang = 'pl', 'de'
        words = ['myśleć', 'ulec', 'obraz']
        Configurations.change_last_used_languages(from_lang, to_lang)
        self.set_input_string(f't {to_lang} -w {" ".join(words)}')

        translations = self.translate()

        correct_translated_words = ['denken', 'erliegen', 'Bild']
        self.assertEqual(len(translations), len(correct_translated_words))
        for i, word in enumerate(words):
            translation = translations[i]
            batch = self.get_nth_translation_batch(0, translation)
            translation_word = self.get_word_from_batch(batch)
            self.assertEqual(word, self.get_constant_part(translation))
            self.assertEqual(translation_word, correct_translated_words[i])

    def test_only_words_args_set(self):
        from_lang, to_lang = 'pl', 'de'
        words = ['myśleć', 'ulec', 'obraz']
        Configurations.change_last_used_languages(from_lang, to_lang)
        self.set_input_string(f't -w {" ".join(words)}')

        translations = self.translate()

        correct_translated_words = ['denken', 'erliegen', 'Bild']
        self.assertEqual(len(translations), len(correct_translated_words))
        for i, word in enumerate(words):
            translation = translations[i]
            batch = self.get_nth_translation_batch(0, translation)
            translation_word = self.get_word_from_batch(batch)
            self.assertEqual(word, self.get_constant_part(translation))
            self.assertEqual(translation_word, correct_translated_words[i])