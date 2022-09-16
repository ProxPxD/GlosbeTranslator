from tests.abstractTranslationTest import AbstractTranslationTest


class MisplacedTest(AbstractTranslationTest):
    def _perform_translation(self):  # TODO: create another class to handle the translation and to be used both in src and tests 
        from_lang = self.argumentParser.from_lang
        to_langs = self.argumentParser.to_langs if self.argumentParser.to_langs else None
        words = self.argumentParser.words if self.argumentParser.words else None
        translations = None

        modes = self.argumentParser.modes
        self.translator.set_from_lang(from_lang)

        if modes.is_multi_lang_mode_on():
            translations = self.translator.multi_lang_translate(words[0], to_langs)
        elif modes.is_multi_word_mode_on():
            translations = self.translator.multi_word_translate(to_langs[0], words)
        elif modes.is_single_mode_on():
            translations = self.translator.single_translate(words[0], to_langs[0])
        elif modes.is_double_multi_mode_on():
            translations = self.translator.double_multi_translate(to_langs, words)
        return translations

    @classmethod
    def _get_mode(cls) -> str | None:
        return 'misplaced'

    test_single_misplaced_once

    test_single_misplaced_twice

    test_single_misplaced_one_arg

    test_multi_langs_misplaced

    test_multi_word_misplaced_one_word

    test_multi_word_misplaced_two_words