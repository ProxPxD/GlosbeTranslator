from argparse import ArgumentParser
from typing import Generator

from argumentParsing.intelligentArgumentParser import Mode, IntelligentArgumentParser
from translating.translatingPrinting.formatter import Formatter


class TranslationPrinter:

    def __int__(self):
        self._formatter = Formatter()

    def print_translations(self, translations: Generator[list[dict, ...], ...], argument_parser: IntelligentArgumentParser):
        translations = self._formatter.format_translations(translations)
        if argument_parser.modes.is_single_mode():
            translation = next(translations)
            self._print_single_translation_mode(translation, argument_parser)
        else:
            self._print_multi_translation_mode(translations, argument_parser)

    def _print_single_translation_mode(self, translation: list[dict, ...], argument_parser: IntelligentArgumentParser):
        print(argument_parser.words[0])
        print(self._formatter.format_translation_into_string(translation))

    def _print_multi_translation_mode(self, translations: Generator[list[dict, ...], ...], argument_parser: IntelligentArgumentParser):
        constant_elem: str = self._get_constant_translation_element(argument_parser)
        variable_elems: list[str, ...] = self._get_variable_elements(argument_parser)

        print(argument_parser.from_lang)
        print(f'{constant_elem}:', end=' ')
        for i, translation in enumerate(translations):
            translation_string = self._formatter.format_translation_into_string(translation)
            print(f'{variable_elems[i]}: {translation_string}')

    def _get_constant_translation_element(self, argument_parser: IntelligentArgumentParser):
        if argument_parser.modes.is_multi_lang_mode():
            return argument_parser.words[0]
        elif argument_parser.modes.is_multi_word_mode():
            return argument_parser.to_langs[0]

    def _get_variable_elements(self, argument_parser: IntelligentArgumentParser):
        if argument_parser.modes.is_multi_lang_mode():
            return argument_parser.to_langs
        elif argument_parser.modes.is_multi_word_mode():
            return argument_parser.words
