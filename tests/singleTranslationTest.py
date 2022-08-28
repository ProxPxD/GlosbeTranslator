from src.translating.argumentParsing.configurations import Configurations
from src.translating.argumentParsing.constants import FLAGS
from src.translating.web.translatorArgumentException import TranslatorArgumentException
from tests.abstractTranslationTest import AbstractTranslationTest


class SingleTranslationTest(AbstractTranslationTest):

    @classmethod
    def _get_mode(cls):
        return FLAGS.SINGLE

    def _perform_translation(self):
        from_lang = self.argumentParser.from_lang
        to_lang = self.argumentParser.to_langs[0] if self.argumentParser.to_langs else None
        word = self.argumentParser.words[0] if self.argumentParser.words else None
        return self.translator.single_translate(word, to_lang, from_lang)

    def test_no_args_set(self):
        self.set_input_string('t')
        self.assertRaises(TranslatorArgumentException, self.translate)

    def test_all_args_set(self):
        tak = 'tak'
        self.set_input_string(f't {tak} pl zh')

        translations = self.translate()
        self.assertTrue(len(translations))

        batch = self.get_nth_translation_batch(0, translations[0])
        translated_word = self.get_word_from_batch(batch)

        self.assertEqual(translations[0][0], tak)
        self.assertTrue(len(batch))
        self.assertTrue(translated_word)

    def test_word_and_to_lang_args_set(self):
        word, from_lang, to_lang = 'ir', 'es', 'pl'
        Configurations.change_last_used_languages(from_lang)
        self.set_input_string(f't {word} {to_lang}')

        translation = self.translate()[0]
        self.assertTrue(len(translation[1]))

        constant_part = self.get_constant_part(translation)
        batch = self.get_nth_translation_batch(0, translation)
        translated_word = self.get_word_from_batch(batch)
        part_of_speech = self.get_part_of_speech_from_batch(batch)

        self.assertEqual(constant_part, word)
        self.assertEqual(translated_word, 'iść')
        self.assertEqual(part_of_speech, 'verb')

    def test_word_arg_set(self):
        word, from_lang, to_lang = 'estar', 'es', 'uk'
        Configurations.change_last_used_languages(from_lang, to_lang)
        self.set_input_string(f't {word}')

        translation = self.translate()[0]
        self.assertTrue(len(translation[1]))

        constant_part = self.get_constant_part(translation)
        batch = self.get_nth_translation_batch(0, translation)
        translated_word = self.get_word_from_batch(batch)
        part_of_speech = self.get_part_of_speech_from_batch(batch)

        self.assertEqual(constant_part, word)
        self.assertEqual(translated_word, 'бути')
        self.assertEqual(part_of_speech, 'verb')
