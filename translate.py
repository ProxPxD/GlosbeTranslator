#!/usr/bin/python3.8
import sys
import requests
from bs4 import BeautifulSoup
import socket
import json

main_url = "glosbe.com"
working_dir = "/home/proxpxd/Desktop/moje_programy/systemowe/glosbeTranslations/"
status = 200


def get_configurations():
    with open(working_dir + 'configurations.txt', 'r') as f:
        lines = json.load(f)
    return lines


def get_conf(name):
    return get_configurations()[name]


def save_conf(conf, value):
    with open(working_dir + 'configurations.txt', 'r') as f:
        lines = json.load(f)

    lines[conf] = value
    with open(working_dir + 'configurations.txt', 'w') as f:
        json.dump(lines, f, indent=4, sort_keys=True)


def create_proper_url(base_url, *args):
    url = ".".join(["https://pl", base_url])
    for part in args:
        url = "/".join([url, part])

    return url


def append_to_dict(data, *keys):
    data_part = data
    for key in keys:
        if key not in data_part:
            data_part[key] = {}
        data_part = data_part[key]

    return data_part


def start_translation(lang1, lang2, word):
    res = get_translations(lang1, lang2, word, with_pronunciation=True)
    if res[1] is not None:
        show_pronunciations(word, res[1])
    show_translations(res[0])


def get_translations(lang1, lang2, word, first_exec=True, with_pronunciation=False):
    global status
    url = create_proper_url(main_url, lang1, lang2, word)
    page = requests.get(url)
    translations = None
    pronunciations = None
    if page.status_code == 200:
        soup = BeautifulSoup(page.text,  "lxml")
        translations = parse_translations(soup)
        pronunciations = parse_pronunciation(soup)
        status = page.status_code
    elif page.status_code == 404:
        print("Not found: ", page.status_code)
        if first_exec:
            print("Starting reverse translating...\n")
            return get_translations(lang2, lang1, word, False)

    elif page.status_code == 429:
        print("Too many requests: ", page.status_code)
        status = page.status_code
    else:
        print("Error: ", page.status_code)
    return [translations, pronunciations]


def parse_translations(soup):
    translations = []
    for header in soup.select('div.translate-entry-translation-header'):
        translation = header.select_one('h4[data-cy="translation"]').text
        translation = translation[0:-1]

        spans = header.select('span.translate-entry-summary-info-text')

        sp = spans[0].text if len(spans) > 1 else None
        gender = None
        for span in spans:
            if "r." in span.text:
                gender = span.text

        translations.append({"translation": translation, "sp": sp, "gender": gender})

    return translations


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
    text = f'{word} ('
    for pron in pronunciations:
        text += pron
        if pron != pronunciations[-1]:
            text += ', '
    text += ')'
    print(text)


# Implementation

def is_connection(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80))
        s.close()
        return True
    except:
        pass
    return False


def save_last_languages(lang1, lang2=None):
    if lang2 is None:
        with open(working_dir + 'last.txt', 'r') as f:
            lang2 = f.readline().split(':')[1]
    with open(working_dir + 'last.txt', 'w') as f:
        f.writelines(f'{lang1}:{lang2}')


def get_last_languages():
    with open(working_dir + 'last.txt', 'r') as f:
        line = f.readline()
    return line.split(':')


def get_all_languages():
    langs = []
    with open(working_dir + 'languages.txt', 'r') as f:
        langs = f.readlines()
    return [l.replace('\n', '') for l in langs]


def update_languages(languages, *used_languages):
    for lang in reversed(used_languages):
        if lang not in languages:
            continue
        languages.remove(lang)
        languages.insert(0, lang)
    with open(working_dir + 'languages.txt', 'w') as f:
        for lang in languages:
            f.write(lang)
            f.write('\n')


def check_and_translate(lang1, lang2, word, with_pronunciation=False):
    if is_connection(main_url):
        return get_translations(lang1, lang2, word, first_exec=False,
                                with_pronunciation=with_pronunciation)
    else:
        print("Brak dostępu do strony")


def foresee_language(word):
    lang = None
    if any(c for c in 'ąęłśńćżź' if c in word):
        lang = 'pl'
    elif any(c for c in 'ôîïèëêâæœ' if c in word):
        lang = 'fr'
    elif any(c for c in 'ñ' if c in word):
        lang = 'es'
    elif any(c for c in 'иъ' if c in word):
        lang = 'ru'
    return lang


def guess_language(word):
    lang = get_last_languages()[0]
    guess = foresee_language(word)
    lang = guess if guess is not None else lang
    return lang


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

        show_translations(result[0])  # Translations
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
    ipa_line = soup.select_one('app-ipa-line')
    if ipa_line is None or len(ipa_line) == 0:
        return None
    return ipa_line.text.replace(' ', '')[:-1].split(',')


def get_arg(i):
    return sys.argv[i] if len(sys.argv) > i else None


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


def print_settings():
    confs = get_configurations()
    for conf in confs:
        print(f'{conf} = {confs[conf]}')


def print_instruction():
    print('Składnia programu:')
    print('trans <word> [[language of word] [target language]] [-r]')
    print('trans cześć pl en')


def main():
    if len(sys.argv) == 1:
        print_instruction()
    elif get_arg(1) == 'set':
        configure()
    elif get_arg(1) == 'show':
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
    else:
        word = get_arg(1)
        lang1 = get_arg(2)
        lang2 = get_arg(3)

        if lang1 is None:
            lang1 = guess_language(word)

        if '-p' in sys.argv:  # get pronunciation
            pronunciations = get_pronunciation(lang1, word)
            show_pronunciations(word, pronunciations)
            update_languages(get_all_languages(), lang1)
        else:
            if get_conf('mode') == 'multi':
                if lang1 is None:
                    lang1 = get_last_languages()[0]
                start_multitranslation(word, lang1, True)
                save_last_languages(lang1)
            elif get_conf('mode') == 'single':
                if lang1 is None:
                    lang1 = get_last_languages()[0]
                if lang2 is None:
                    lang2 = get_last_languages()[1]
                if '-r' in sys.argv:
                    lang1, lang2 = lang2, lang1
                start_translation(lang1, lang2, word)
                update_languages(get_all_languages(), lang1, lang2)
                save_last_languages(lang1, lang2)




if __name__ == '__main__':
    main()
