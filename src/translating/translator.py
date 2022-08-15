from typing import Generator

import requests

from .parsing.parser import Parser
from .web.connector import Connector
from .web.translatorArgumentException import TranslatorArgumentException


def _no_nones(func):
    def wrap(*args):
        return (elem for elem in func(*args) if elem and elem[1] is not None)
    return wrap


class Translator:

    def __init__(self, from_lang: str = None, to_lang: str = None, word: str = None):
        self._connector: Connector = Connector(from_lang, to_lang, word)
        self._parser: Parser = Parser()
        self._html: str = ""

    def set_from_lang(self, from_lang: str) -> None:
        self._connector.set_from_lang(from_lang)

    def set_to_lang(self, to_lang: str) -> None:
        self._connector.set_to_lang(to_lang)

    @_no_nones
    def multi_lang_translate(self, word: str, to_langs: list[str, ...], from_lang: str = None) -> Generator[tuple[str, list], None, None]:
        if not word:
            raise TranslatorArgumentException(word)  # TODO add exception if no word
        if from_lang:
            self.set_from_lang(from_lang)
        self._connector.establish_session()
        for to_lang in to_langs:
            yield to_lang, self._generate_translation(word, to_lang)
        self._connector.close_session()

    @_no_nones
    def multi_word_translate(self, to_lang, words: list[str, ...], from_lang: str = None) -> Generator[tuple[str, list], None, None]:
        if from_lang:
            self.set_from_lang(from_lang)
        self._connector.establish_session()
        for word in words:
            yield word, self._generate_translation(word, to_lang)
        self._connector.close_session()

    @_no_nones
    def single_translate(self, word: str, to_lang: str = None, from_lang: str = None) -> Generator[tuple[str, list], None, None]:
        if from_lang:
            self.set_from_lang(from_lang)
        self._connector.establish_session()
        yield word, self._generate_translation(word, to_lang)
        self._connector.close_session()

    def _generate_translation(self, word: str, to_lang: str = None) -> list:
        self._connector.set_word(word)
        if to_lang:
            self.set_to_lang(to_lang)
        return self._translate_from_attributes()

    def _translate_from_attributes(self) -> list:
        page: requests.Response = self._connector.get_page()
        self._parser.set_page(page)
        return self._parser.parse()
