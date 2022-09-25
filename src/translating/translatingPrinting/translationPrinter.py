import logging

from src.translating.argumentParsing.translatorParser import TranslatorParser
from .formatter import Formatter
from ..constants import LogMessages


class TranslationPrinter:

    _post_sep_length = 64
    _pre_sep_length = 4

    def __init__(self):
        self._formatter = Formatter()

    def print_translations(self, translations, argument_parser: TranslatorParser):
        translations = self._formatter.format_translations(translations)
        if argument_parser.modes.is_single_mode_on():
            translation = next(translations)[1]
            self._print_single_translation_mode(translation, argument_parser)
        else:
            self._print_multi_translation_mode(translations, argument_parser)

    def _print_single_translation_mode(self, translation: list[dict, ...], argument_parser: TranslatorParser):
        if len(translation):
            print(argument_parser.words[0])
            print(self._formatter.format_translation_into_string(translation))

    def _print_multi_translation_mode(self, translations, argument_parser: TranslatorParser):
        constant_elem: str = self._get_constant_translation_element(argument_parser)
        starting_msg: str = f'{argument_parser.from_lang} -- {constant_elem}:' if constant_elem else f'{argument_parser.from_lang}:'

        print(starting_msg)
        for marker, translation in translations:
            translation_msg = self._get_message_for_translation(translation)
            section = self._get_section(marker)
            variable_elem = self._get_variable_elem(marker)

            if section:
                print('-' * self._pre_sep_length, section, '-' * self._post_sep_length)
            print(f'{variable_elem}: {translation_msg}')

    def _get_message_for_translation(self, translation):
        if len(translation):
            translation_string = self._formatter.format_translation_into_string(translation)
        else:
            translation_string = LogMessages.NO_TRANSLATION
            logging.warning(LogMessages.NO_TRANSLATION)
        return translation_string

    def _get_section(self, marker: tuple|str, sections=[]):
        if isinstance(marker, tuple) and marker[0] not in sections:
            sections.append(marker[0])
            return marker[0]
        return None

    def _get_variable_elem(self, marker: tuple|str):
        if isinstance(marker, tuple):
            return marker[1]
        return marker

    def _get_constant_translation_element(self, argument_parser: TranslatorParser):
        if argument_parser.modes.is_multi_lang_mode_on():
            return argument_parser.words[0]
        elif argument_parser.modes.is_multi_word_mode_on():
            return argument_parser.to_langs[0]
        return ''
