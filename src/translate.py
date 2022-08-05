#!/usr/bin/python
import logging
import socket
import sys
from dataclasses import dataclass

from translating.argumentParsing import configurations
from translating.argumentParsing.configurations import Configurations
from translating.argumentParsing.intelligentArgumentParser import IntelligentArgumentParser
from translating.argumentParsing.modeManager import FullModes, ModesManager
from translating.constants import LogMessages
from translating.translatingPrinting.translationPrinter import TranslationPrinter
from translating.translator import Translator
from translating.web.wrongStatusCodeException import WrongStatusCodeException


# TODO: implement one constant connection throughout the whole translation process



@dataclass(frozen=True)
class Data:
    LOG_PATH = configurations.Paths.RESOURCES_DIR / 'logs.txt'


def main():
    logging.basicConfig(filename=Data.LOG_PATH, encoding='utf-8', level=logging.WARNING,
                        format='%(levelname)s: %(message)s ')
    if len(sys.argv) == 1:
        sys.argv = get_test_arguments()

    try:
        Configurations.init()
        argument_parser = IntelligentArgumentParser(sys.argv)
        argument_parser.parse()
        if argument_parser.modes.is_any_display_mode_on():
            display_information(argument_parser)
        if argument_parser.modes.is_any_configurational_mode_on():
            set_config(argument_parser)
        if argument_parser.is_translation_mode_on():
            translate(argument_parser)

        if not argument_parser.modes.is_any_display_mode_on():
            Configurations.save()

    except WrongStatusCodeException as err:
        logging.error(f'{err.page.status_code}: {err.page.text}')
        print(LogMessages.UNKNOWN_PAGE_STATUS.format(err.page.status_code))


def get_test_arguments():
    return 't think en pl'.split(' ')


def translate(argument_parser: IntelligentArgumentParser):
    translations = get_translations(argument_parser)
    translation_printer = TranslationPrinter()
    translation_printer.print_translations(translations, argument_parser)
    Configurations.change_last_used_languages(argument_parser.from_lang, *argument_parser.to_langs)


def get_translations(argument_parser: IntelligentArgumentParser):
    translator = Translator(argument_parser.from_lang)
    modes = argument_parser.modes
    translations = None
    if modes.is_multi_lang_mode_on():
        translations = translator.multi_lang_translate(argument_parser.words[0], argument_parser.to_langs)
    elif modes.is_multi_word_mode_on():
        translations = translator.multi_word_translate(argument_parser.to_langs[0], argument_parser.words)
    elif modes.is_single_mode_on():
        translations = translator.single_translate(argument_parser.words[0], argument_parser.to_langs[0])

    return translations


def display_information(argument_parser: IntelligentArgumentParser):
    for to_display in argument_parser.modes.get_display_modes_turned_on():
        if to_display == FullModes.SETTINGS:
            display_configs(FullModes.DEFAULT_TRANSLATIONAL_MODE, FullModes.LANG_LIMIT, FullModes.SAVED_LANGS)
            continue
        if to_display == FullModes.HELP:
            ModesManager.show_help()
            continue
        display_config(to_display)


def display_configs(*config_names: str):  # TODO, not here: implement help and input modes validation
    for to_display in config_names:
        display_config(to_display)


def display_config(config_name: str):
    conf_to_display = Configurations.get_conf(config_name)
    if isinstance(conf_to_display, list):
        conf_to_display = str(conf_to_display)[1:-1].replace("'", '')
    print(f'{config_name[2:]}: {conf_to_display}')


def set_config(argument_parser: IntelligentArgumentParser):
    for config_name in argument_parser.modes.get_configurational_modes_turned_on():
        arguments = argument_parser.modes.get_config_args(config_name)
        Configurations.change_conf(config_name, arguments[0])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
