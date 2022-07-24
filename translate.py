#!/usr/bin/python
import socket
import sys

import requests
from bs4 import BeautifulSoup

from argumentParsing.configurations import save_last_used_languages
from argumentParsing.intelligentArgumentParser import IntelligentArgumentParser, Mode
from translating.translator import Translator


def start_translation(lang1, lang2, word):
    res = get_translations(lang1, lang2, word, with_pronunciation=True)

    if res[1] is not None:
        show_pronunciations(word, res[1])
    show_translations(res[0])


# Temporary don't remove an argument
# def get_translations(lang1, lang2, word, first_exec=True, with_pronunciation=False):
#     pronunciations = parse_pronunciation(soup)

# start show

def show_translations(translations):
    if translations is None:
        print()
        return
    for trans in translations:
        text = show_translation(trans)
        if trans != translations[-1]:
            print(text, end=', ')
        else:
            print(text)


def format_gender(gender):
    if 'ż' in gender:
        gender = 'fem'
    elif 'ę' in gender:
        gender = 'masc'
    elif 'nijaki' in gender:
        gender = 'neut'
    return gender


def format_part_of_speech(sp):
    if 'rzecz' in sp:
        sp = 'noun'
    if 'czas' in sp:
        sp = 'verb'
    if 'przym' in sp:
        sp = 'adv.'
    return sp


def show_translation(trans):
    gender = trans["gender"]
    sp = trans["sp"]
    translation = trans["translation"]
    text = translation
    if gender is not None:
        text += f' [{format_gender(gender)}]'
    if sp is not None:
        text += f' ({format_part_of_speech(sp)})'
    return text


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


def find_pronunciation(lang1, word):
    lang2 = 'en' if lang1 != 'en' else 'es'
    global status
    url = create_proper_url(main_url, lang1, lang2, word)
    page = requests.get(url)
    pronunciations = None

    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "lxml")
        pronunciations = parse_pronunciation(soup)
        status = page.status_code
    elif page.status_code == 404:
        print("Not found: ", page.status_code)
    return pronunciations


def parse_pronunciation(soup):
    pronunciations = []
    summaries = soup.findAll('span', {'class': 'phrase__summary__field'})
    for summary in summaries:
        if summary.text[-1] in ']/':
            pronunciations.append(summary.text.replace(' ', '')[1:-1])
    return pronunciations

# start config
def configure():
    if get_arg(2) == 'limit':
        new_limit = get_arg(3)
        save_conf('language_limit', int(new_limit))
    elif get_arg(2) == 'mode':
        new_mode = get_arg(3)
        if new_mode in ['multi', '-1', '0']:
            save_conf('mode', 'multi')
        elif new_mode in ['single', '1']:
            save_conf('mode', 'single')

# end config

#start printing


def print_settings():
    confs = get_configurations()
    for conf in confs:
        print(f'{conf} = {confs[conf]}')


def display_to_user(to_show=None):
    if to_show is None:
        to_show = get_arg(2)
    if to_show == 'settings':
        print_settings()
    elif to_show == 'last':
        lang1, lang2 = tuple(get_last_languages())
        print(lang1, '=>', lang2)
    elif to_show == 'languages':
        langs = get_all_languages()
        for lang in langs:
            print(lang, end='')
            if lang != langs[-1]:
                print(', ', end='')
        print()
    elif to_show == 'mode':
        print(f'mode = {get_configurations()["mode"]}')


def print_help():
    print_instruction()


def print_instruction():
    print('Składnia programu:')
    print('trans <word> [[language of word] [target language]] [-r]')
    print('trans cześć pl en')

    print()
    print('-l    : sets multitranslation language limit')
    print('-m    : sets mode (multitranslation or single)')
    print('-ll   : show all displaying languages')
    print('-last : show last used languages')
    print('-ss   : shows settings')
    print('trans -s settings/last/languages')

#end printing

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


def set_instructions():
    if get_arg(1) == '-help' or '-h' in sys.argv:
        print_help()
    elif get_arg(1) == '-l':
        new_limit = get_arg(2)
        if new_limit is None:
            print('The limit has to be entered')
            return
        save_conf('language_limit', int(new_limit))
    elif get_arg(1) == '-m':
        new_mode = get_arg(2)
        if new_mode in ['multi', '-1', '0']:
            save_conf('mode', 'multi')
        elif new_mode in ['single', '1']:
            save_conf('mode', 'single')
    elif get_arg(1) == '-ll':
        display_to_user('languages')
    elif get_arg(1) == '-last':
        display_to_user('last')
    elif get_arg(1) == '-ss':
        print_settings()
    elif get_arg(1) == '-show' or get_arg(1) == '-s':
        display_to_user()
    elif get_arg(1) == '-loop':
        translation_loop()


def main():
    if len(sys.argv) == 1:
        sys.argv = get_test_arguments()
    argumentParser = IntelligentArgumentParser(sys.argv)
    argumentParser.parse()
    translations = get_translations(argumentParser)
    for t in translations:
        print(t)
    # print(translations)

    # save_last_used_languages(argumentParser.from_lang, *argumentParser.to_langs)


def get_test_arguments():
    return ['trans', 'anioł', 'pl', 'fr']


def get_translations(argumentParser: IntelligentArgumentParser):
    translator = Translator(argumentParser.from_lang)
    modes = argumentParser.modes
    translations = None
    if modes.is_multi_lang_mode():
        translations = translator.multi_lang_translate(argumentParser.words[0], argumentParser.to_langs)
    elif modes.is_multi_word_mode():
        translations = translator.multi_word_translate(argumentParser.words, argumentParser.to_langs[0])
    elif modes.is_single_mode():
        translations = translator.single_translate(argumentParser.words[0], argumentParser.to_langs[0])

    return translations


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
