import logging
import traceback
from dataclasses import dataclass, field, replace
from itertools import product
from typing import Iterable

import requests
import requests.exceptions as request_exceptions

from .parsing.parser import Parser, Record, WrongStatusCodeError
from .web.connector import Connector, TransArgs, TranslatorArgumentException


@dataclass(frozen=True)
class TranslationTypes:
    SINGLE = 'Single'
    LANG = 'Lang'
    WORD = 'Word'
    DOUBLE = 'Double'


@dataclass
class TranslationResult:
    trans_args: TransArgs = field(default_factory=lambda: TransArgs())
    records: Iterable[Record] = field(default_factory=lambda: [])
    type = TranslationTypes.SINGLE


@dataclass(frozen=True)
class PageCodeMessages:
    PLEASE_REPORT = 'Please, report the case'
    UNHANDLED_PAGE_FULL_MESSAGE = 'Unhandled page code: {}! ' + PLEASE_REPORT
    PAGE_NOT_FOUND_404 = 'Page has not been found (404). Please, check the arguments: {}'  # if the command is correct. Words: {}, glosbe from: , glosbe to:
    PAGE_NOT_FOUND_303 = 'The page has to be redirected (303). ' + PLEASE_REPORT


class ErrorMessages:
    NO_TRANSLATION = 'No translation has been found. Either the arguments were invalid or the requested translation does not exist so far'
    INVALID_ARGUMENT = 'Error! An argument has not been set {}'
    EXCEEDED_NUMBER_OF_RETRIES = 'Error! Exceeded maximum number of retries - check your network connection'
    CONNECTION_ERROR = 'Connection error! Check your network connection'


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
        except WrongStatusCodeError as err:
            logging.error(f'{err.page.status_code}: {err.page.text}')
            return TranslationResult(trans_args, [Record(self._get_status_code_message(err))])
        except TranslatorArgumentException:
            logging.exception(f'Exception: Invalid argument {str(trans_args)}')
            return TranslationResult(trans_args, [Record(ErrorMessages.INVALID_ARGUMENT.format(str(trans_args)))])
        except request_exceptions.ConnectionError as err:
            logging.exception(traceback.format_exc())
            return TranslationResult(trans_args, [Record(ErrorMessages.CONNECTION_ERROR)])
        return TranslationResult(trans_args, records)

    def _translate_from_attributes(self) -> Iterable[Record]:
        page: requests.Response = self._connector.get_page()
        self._parser.set_page(page)
        return self._parser.parse()

    def _get_status_code_message(self, err: WrongStatusCodeError) -> str:
        match err.page.status_code:
            case 404:
                return PageCodeMessages.PAGE_NOT_FOUND_404.format(str(self._connector.trans_args))
            case 303:
                return PageCodeMessages.PAGE_NOT_FOUND_303
            case _:
                return PageCodeMessages.UNHANDLED_PAGE_FULL_MESSAGE.format(err.page.status_code)
