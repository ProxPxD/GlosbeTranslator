import requests

from .parsing.parser import Parser
from .web.connector import Connector


def _no_nones(func):
    def wrap(*args):
        return (elem for elem in func(*args) if elem and elem[1] is not None)
    return wrap


class Translator:

    def __init__(self, from_lang: str, to_lang: str = None, word: str = None):
        self._connector: Connector = Connector(from_lang, to_lang, word)
        self._parser: Parser = Parser()
        self._html: str = ""

    def set_to_lang(self, to_lang: str):
        self._connector.set_to_lang(to_lang)

    @_no_nones
    def multi_lang_translate(self, word: str, to_langs: list[str, ...]):
        return ((to_lang, self._generate_translation(word, to_lang)) for to_lang in to_langs)

    @_no_nones
    def multi_word_translate(self, to_lang, words: list[str, ...]):
        return ((word, self._generate_translation(word, to_lang)) for word in words)

    @_no_nones
    def single_translate(self, word: str, to_lang: str = None):
        return ((to_lang, self._generate_translation(word, to_lang)) for _ in [0])

    def _generate_translation(self, word: str, to_lang: str = None):
        self._connector.set_word(word)
        if to_lang:
            self.set_to_lang(to_lang)
        return self._translate_from_attributes()

    def _translate_from_attributes(self):
        page: requests.Response = self._connector.get_page()
        if page:
            self._parser.set_page_text(page.text)
        return self._parser.parse()
