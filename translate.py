#!/usr/bin/python3
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
    url = "https://" + base_url
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


def parse_translations(soup):
    translations = []
    for header in soup.findAll('li', {'data-element': 'translation'}):
        sp = None
        gender = None
        try:
            translation = header.select_one('span[data-element="phrase"]').text[1:-1]
        except Exception:
            continue
        spans = header.findAll('span', {'class': 'phrase__summary__field'})
        spans = [s.text for s in spans]
        if len(spans) > 0:
            sp = spans[0]
        if len(spans) > 1:
            gender = spans[1]

        translations.append({"translation": translation, "sp": sp, "gender": gender})

    return translations


# Temporary don't remove an argument
def get_translations(lang1, lang2, word, first_exec=True, with_pronunciation=False):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Dnt': '1',
        'Host': 'httpbin.org',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.97 Safari/537.36',
        'X-Amzn-Trace-Id': 'Root=1-5ee7bbec-779382315873aa33227a5df6'}

    global status
    url = create_proper_url(main_url, lang1, lang2, word)
    s = requests.Session()
    s.headers.update({'User-agent': 'Mozilla/5.0'})
    page = s.get(url, allow_redirects=False)
    s.close()
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
    elif page.status_code == 301:
        print("Moved permanently: ", page.status_code)
        status = page.status_code
    else:
        print("Error: ", page.status_code)
        print(page.text)
    return [translations, pronunciations]


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
        if len(result[0]) != 0:
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


def get_arg(i, args=None):
    if args is None:
        args = sys.argv
    return args[i] if len(args) > i else None


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


def main():
    #sys.argv = ['trans' for i in range(4)]
    #sys.argv[1] = 'trzymać'
    #sys.argv[2] = 'pl'
    #sys.argv[3] = 'uk'
    args = sys.argv
    mode = ''
    if len(args) == 1:
        print_instruction()
    elif get_arg(1) == '-help' or '-h' in sys.argv:
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
    else:  # End of settings
        if '-0' in args or '-m' in args:
            mode = 'multi'
        if '-1' in args:
            mode = 'single'
        [args.remove(tag) for tag in ['-0', '-m', '-1'] if tag in args]

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
            if (get_conf('mode') == 'multi' and lang2 is None) or mode == 'multi':
                if lang1 is None:
                    lang1 = get_last_languages()[0]
                start_multitranslation(word, lang1, True)
                save_last_languages(lang1)
            elif (get_conf('mode') == 'single' or lang2 is not None) or mode == 'single':
                if lang1 is None:
                    lang1 = get_last_languages()[0]
                if lang2 is None:
                    lang2 = get_last_languages()[1]
                    if lang2 == lang1:
                        lang2 = get_last_languages()[0]
                if '-r' in sys.argv:
                    lang1, lang2 = lang2, lang1
                start_translation(lang1, lang2, word)
                update_languages(get_all_languages(), lang1, lang2)
                save_last_languages(lang1, lang2)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
