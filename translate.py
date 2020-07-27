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
        spans = header.select('span.translate-entry-summary-info-text')

        sp = spans[0].text if len(spans) > 1 else None
        gender = None
        for span in spans:
            if "r." in span.text:
                gender = span.text

        translations.append({"translation": translation, "sp": sp, "gender": gender})

    return translations


def show_translations(translations):
    for trans in translations:
        show_translation(trans)


def show_translation(trans):
    gender = trans["gender"]
    sp = trans["sp"]
    translation = trans["translation"]

    if gender is not None and sp is not None:
        print(translation + "[" + gender + "] (" + sp + ")")
    elif gender is not None:
        print(translation + " (" + gender + ")")
    elif sp is not None:
        print(translation + " (" + sp + ")")
    else:
        print(translation)


def translate(lang1, lang2, word, showing=False):
    translations = get_translations(lang1, lang2, word)
    if showing:
        show_translations(translations)
    words = set((lang2, trans["translation"]) for trans in translations)
    return words


def is_connection(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80))
        s.close()
        return True
    except:
        pass
    return False


def save_languages(lang1, lang2):
    with open(working_dir + 'last.txt', 'w') as f:
        f.writelines(lang1 + lang2)


def get_last_languages():
    with open(working_dir + 'last.txt', 'r') as f:
        line = f.readlines()[0]
    return line[:2], line[2:]


def check_and_translate(lang1, lang2, word, showing=False):
    if is_connection(main_url):
        translate(lang1, lang2, word, showing)
    else:
        print("Brak dostępu do strony")


def main():
    if len(sys.argv) == 1:
        print('Składnia programu:')
        print('trans <word> [[language of word] [target language]] [-r]')
        print('trans cześć pl en')
    elif len(sys.argv) in [2, 3]:
        lang1, lang2 = get_last_languages()
        word = sys.argv[1]
        if '-r' in sys.argv:
            lang1, lang2 = lang2, lang1
        print("translating {} from {} to {}...".format(word, lang1, lang2))
        check_and_translate(lang1, lang2, word, True)
    elif len(sys.argv) >= 4:
        lang1 = sys.argv[2]
        lang2 = sys.argv[3]
        word = sys.argv[1]
        if '-r' in sys.argv:
            lang1, lang2 = lang2, lang1
        check_and_translate(lang1, lang2, word, True)
        save_languages(lang1, lang2)


if __name__ == '__main__':
    main()
