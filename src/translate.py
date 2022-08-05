#!/usr/bin/python
import logging
import socket
import sys
from dataclasses import dataclass

from bs4 import BeautifulSoup

from translating.argumentParsing import configurations
from translating.argumentParsing.configurations import Configurations
from translating.argumentParsing.intelligentArgumentParser import IntelligentArgumentParser
from translating.argumentParsing.modeManager import FullModes, ModesManager
from translating.constants import LogMessages
from translating.translatingPrinting.translationPrinter import TranslationPrinter
from translating.translator import Translator
from translating.web.wrongStatusCodeException import WrongStatusCodeException



def show_pronunciations(word, pronunciations):
    if pronunciations is None:
        return None
    text = f'{word} '
    for pron in pronunciations:
        text += f'/{pron}/'
        if pron != pronunciations[-1]:
            text += ', '
    print(text)

# end show


# Implementation

# start connect

def is_connection(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80))
        s.close()
        return True
    except:
        pass
    return False

# end connect


def check_and_translate(lang1, lang2, word, with_pronunciation=False):
    if is_connection(main_url):
        return get_translations(lang1, lang2, word, first_exec=False,
                                with_pronunciation=with_pronunciation)
    else:
        print("Brak dostępu do strony")


def get_pronunciation(lang, word):
    if is_connection(main_url):
        return find_pronunciation(lang, word)
    else:
        print("Brak dostępu do strony")


def start_multitranslation(word, lang1, with_pronunciation):
    language_limit = get_conf('language_limit')
    languages = get_all_languages()
    for lang in languages[:language_limit+1]:
        if lang == lang1:
            continue
        result = check_and_translate(lang1, lang, word, with_pronunciation)
        if with_pronunciation and result[1] is not None:
            with_pronunciation = False
            show_pronunciations(word, result[1])  # Pronunciations

        print(f'{lang}:', end=' ')
        if result[0] is not None and len(result[0]) != 0:
            show_translations(result[0])  # Translations
        else:
            print()
    update_languages(languages, lang1)
###Pronunciation


def parse_pronunciation(soup):
    pronunciations = []
    summaries = soup.findAll('span', {'class': 'phrase__summary__field'})
    for summary in summaries:
        if summary.text[-1] in ']/':
            pronunciations.append(summary.text.replace(' ', '')[1:-1])
    return pronunciations


def translation_loop():
    langs = get_last_languages()
    lang1 = langs[0]
    lang2 = langs[1]
    mode = get_conf('mode')
    in_loop = True
    print('Please enter a word')
    if mode == 'single':
        print(f'trans ? {lang1} {lang2}')
    else:
        print(f'trans ? {lang1}')
    while in_loop:
        word = input()
        if word[:2] in ['l1', '-l1']:
            lang1 = word[3:]
            print(f'trans ? {lang1} {lang2}')
        elif word[:2] in ['l2', '-l2']:
            lang2 = word[3:]
            print(f'trans ? {lang1} {lang2}')
        elif word[:2] in ['-m', '-0', 'm', '0']:
            mode = 'multi'
            print(f'trans ? {lang1}')
        elif word[:2] in ['-1', '1']:
            mode = 'single'
            print(f'trans ? {lang1} {lang2}')
        elif word[:2] in ['-r', 'r']:
            lang1, lang2 = lang2, lang1
            print(f'trans ? {lang1} {lang2}')
        elif word[:2] in ['-q', 'q']:
            in_loop = False
        else:
            if len(word) > 0:
                if mode == 'multi':
                    start_multitranslation(word, lang1, True)
                else:
                    start_translation(lang1, lang2, word)
                print('—' * 30)


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
