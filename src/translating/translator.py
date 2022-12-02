from dataclasses import dataclass, field, replace
from itertools import product
from typing import Iterable

import requests

from .parsing.parser import Parser, Record
from .web.connector import Connector, TransArgs
from .web.exceptions import WrongStatusCodeException


@dataclass(frozen=True)
class TranslationTypes:
    SINGLE = 'Single'
    LANG = 'Lang'
    WORD = 'Word'
    DOUBLE = 'Double'


@dataclass
class TranslationResult:
    trans_args = TransArgs()
    records: list[Record] | WrongStatusCodeException = field(default_factory=lambda: [])
    type = TranslationTypes.SINGLE


class Translator:

    def __init__(self, from_lang: str = None, to_lang: str = None, word: str = None):
        self._connector: Connector = Connector(from_lang, to_lang, word)
        self._parser: Parser = Parser()

    def set_from_lang(self, from_lang: str) -> None:
        self._connector.trans_args.from_lang = from_lang

    def set_to_lang(self, to_lang: str) -> None:
        self._connector.trans_args.to_lang = to_lang

    def multi_lang_translate(self, word: str, to_langs: list[str, ...], from_lang: str = None) -> Iterable[TranslationResult]:
        if from_lang:
            self.set_from_lang(from_lang)
        self._connector.establish_session()
        for to_lang in to_langs:
            yield self._translate_as_result(word, to_lang)
        self._connector.close_session()

    def multi_word_translate(self, to_lang, words: list[str, ...], from_lang: str = None) -> Iterable[TranslationResult]:
        if from_lang:
            self.set_from_lang(from_lang)
        self._connector.establish_session()
        for word in words:
            yield self._translate_as_result(word, to_lang)
        self._connector.close_session()

    def single_translate(self, word: str, to_lang: str = None, from_lang: str = None) -> Iterable[TranslationResult]:
        if from_lang:
            self.set_from_lang(from_lang)
        self._connector.establish_session()
        yield self._translate_as_result(word, to_lang)
        self._connector.close_session()

    def double_multi_translate(self, to_langs, words: list[str, ...], from_lang: str = None, by_word=False) -> Iterable[TranslationResult]:
        if from_lang:
            self.set_from_lang(from_lang)

        self._connector.establish_session()
        langs_words = self._get_product(to_langs, words, by_word)
        for to_lang, word in langs_words:
            yield self._translate_as_result(word, to_lang)

        self._connector.close_session()

    def _get_product(self, to_langs, words, by_word=False):
        if by_word:
            return map(tuple, map(reversed, product(words, to_langs)))
        return product(to_langs, words)

    def _translate_as_result(self, word: str, to_lang: str = None) -> TranslationResult:
        self._connector.trans_args.word = word
        if to_lang:
            self.set_to_lang(to_lang)

        trans_args = replace(self._connector.trans_args)
        try:
            records = self._translate_from_attributes()
        except WrongStatusCodeException as ex:
            return TranslationResult(trans_args, ex)
        return TranslationResult(trans_args, records)

    def _translate_from_attributes(self) -> list[Record]:
        page: requests.Response = self._connector.get_page()
        self._parser.set_page(page)
        return self._parser.parse()
