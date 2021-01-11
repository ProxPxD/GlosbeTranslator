#!/usr/bin/python3.8
import sys
import requests
from bs4 import BeautifulSoup
import socket

main_url = "glosbe.com"
working_dir = "/home/proxpxd/Desktop/moje_programy/systemowe/glosbeTranslations/"
status = 200


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


def get_translations(lang1, lang2, word, first_exec=True):
    global status
    url = create_proper_url(main_url, lang1, lang2, word)
    page = requests.get(url)
    translations = []

    if page.status_code == 200:
        soup = BeautifulSoup(page.text,  "lxml")
        translations = parse_translations(soup)
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

    return translations


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


def translate(lang1, lang2, word):
    translations = get_translations(lang1, lang2, word)
    return translations


def is_connection(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80))
        s.close()
        return True
    except:
        pass
    return False


def save_language(lang1):
    with open(working_dir + 'last.txt', 'w') as f:
        f.writelines(lang1)


def get_last_language():
    with open(working_dir + 'last.txt', 'r') as f:
        line = f.readlines()[0]
    return line[:2]


def read_languages():
    langs = []
    with open(working_dir + 'languages.txt', 'r') as f:
        langs = f.readlines()
    return [l.replace('\n', '') for l in langs]


def update_languages(languages, lang):
    if lang not in languages:
        return
    languages.remove(lang)
    languages.insert(0, lang)
    with open(working_dir + 'languages.txt', 'w') as f:
        for lang in languages:
            f.write(lang)
            f.write('\n')



def check_and_translate(lang1, lang2, word):
    if is_connection(main_url):
        return get_translations(lang1, lang2, word, False)
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
    return lang


def start_multitranslation(word, lang1):
    languages = read_languages()
    for lang in languages:
        if lang == lang1:
            continue
        # print("translating {} from {} to {}...".format(word, lang1, lang))
        print(f'{lang}: ', end='')
        translations = check_and_translate(lang1, lang, word)
        show_translations(translations)
    update_languages(languages, lang1)


def get_arg(i):
    return sys.argv[i] if len(sys.argv) > i else None


def main():
    if len(sys.argv) == 1:
        print('Składnia programu:')
        print('trans <word> [[language of word] [target language]] [-r]')
        print('trans cześć pl en')
    else:
        word = get_arg(1)
        lang1 = get_arg(2)
        lang2 = get_arg(3)
        if lang1 is None:
            lang1 = get_last_language()
            guess = foresee_language(word)
            lang1 = guess if guess is not None else lang1
        if lang2 is None:
            start_multitranslation(word, lang1)
        else:
            if '-r' in sys.argv:
                lang1, lang2 = lang2, lang1
            res = translate(lang1, lang2, word)
            show_translations(res)


if __name__ == '__main__':
    main()
