import logging

from argumentParsing.intelligentArgumentParser import IntelligentArgumentParser
from translating.constants import LogMessages
from translating.translatingPrinting.formatter import Formatter


class TranslationPrinter:

    def __init__(self):
        self._formatter = Formatter()

    def print_translations(self, translations, argument_parser: IntelligentArgumentParser):
        translations = self._formatter.format_translations(translations)
        if argument_parser.modes.is_single_mode_on():
            translation = next(translations)[1]
            self._print_single_translation_mode(translation, argument_parser)
        else:
            self._print_multi_translation_mode(translations, argument_parser)

    def _print_single_translation_mode(self, translation: list[dict, ...], argument_parser: IntelligentArgumentParser):
        if len(translation):
            print(argument_parser.words[0])
            print(self._formatter.format_translation_into_string(translation))

    def _print_multi_translation_mode(self, translations, argument_parser: IntelligentArgumentParser):
        constant_elem: str = self._get_constant_translation_element(argument_parser)

        print(f'{argument_parser.from_lang} -- {constant_elem}:')
        for variable_elem, translation in translations:
            if len(translation):
                translation_string = self._formatter.format_translation_into_string(translation)
            else:
                translation_string = LogMessages.NO_TRANSLATION
                logging.warning(LogMessages.NO_TRANSLATION)
            print(f'{variable_elem}: {translation_string}')

    def _get_constant_translation_element(self, argument_parser: IntelligentArgumentParser):
        if argument_parser.modes.is_multi_lang_mode_on():
            return argument_parser.words[0]
        elif argument_parser.modes.is_multi_word_mode_on():
            return argument_parser.to_langs[0]
