from src.translating.constants import TranslationParts
from src.translating.web.translatorArgumentException import TranslatorArgumentException
from tests.AbstractTranslationTest import AbstractTranslationTest


class SingleTranslationTest(AbstractTranslationTest):

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
        self.assertEqual(translations[0][0], tak)
        self.assertTrue(len(translations[0][1]))
        self.assertTrue(len(translations[0][1][0][TranslationParts.TRANSLATION]))

    def test_word_and_to_lang_args_set(self):
        self.set_input_string('t ir es')

    def test_word_arg_set(self):
        self.set_input_string('t ')