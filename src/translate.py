import logging
import sys
from dataclasses import dataclass

from translating.argumentParsing.abstractParsing.src.parsingException import ParsingException
from translating.argumentParsing.translatorParser import TranslatorParser
from translating.configs import configChanger, configurations, configDisplayer
from translating.configs.configurations import Configurations
from translating.constants import LogMessages
from translating.translatingPrinting.translationPrinter import TranslationPrinter
from translating.translator import Translator
from translating.web.wrongStatusCodeException import WrongStatusCodeException


@dataclass(frozen=True)
class Data:
    LOG_PATH = configurations.Paths.RESOURCES_DIR / 'logs.txt'


def main():
    if len(sys.argv) == 1:
        sys.argv = get_test_arguments()

    try:
        Configurations.init()
        logging.basicConfig(filename=Data.LOG_PATH, encoding='utf-8', level=logging.WARNING,
                            format='%(levelname)s: %(message)s ')
        argument_parser = TranslatorParser(sys.argv)
        argument_parser.parse()
        if argument_parser.modes.is_any_displayable_mode_on():
            configDisplayer.display_information(argument_parser)
        if argument_parser.modes.is_any_configurational_mode_on():
            configChanger.set_configs(argument_parser)
        if argument_parser.is_translation_mode_on():
            translate_and_print(argument_parser)

        if not argument_parser.modes.is_any_displayable_mode_on():
            Configurations.save()

    except WrongStatusCodeException as err:
        logging.error(f'{err.page.status_code}: {err.page.text}')
        print(LogMessages.UNKNOWN_PAGE_STATUS.format(err.page.status_code))
    except ParsingException as err:
        for msg in err.validation_messages:
            print(msg)


def get_test_arguments():
    return 't -la'.split(' ')  # t laborious en uk


def translate_and_print(argument_parser: TranslatorParser):
    translations = get_translations(argument_parser)
    translation_printer = TranslationPrinter()
    translation_printer.print_translations(translations, argument_parser)
    Configurations.change_last_used_languages(argument_parser.from_lang, *argument_parser.to_langs)


def get_translations(argument_parser: TranslatorParser):
    translator = Translator(argument_parser.from_lang)
    modes = argument_parser.modes
    translations = None
    if modes.is_multi_lang_mode_on():
        translations = translator.multi_lang_translate(argument_parser.words[0], argument_parser.to_langs)
    elif modes.is_multi_word_mode_on():
        translations = translator.multi_word_translate(argument_parser.to_langs[0], argument_parser.words)
    elif modes.is_single_mode_on():
        translations = translator.single_translate(argument_parser.words[0], argument_parser.to_langs[0])
    elif modes.is_double_multi_mode_on():
        translations = translator.double_multi_translate(argument_parser.to_langs, argument_parser.words)

    return translations


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
