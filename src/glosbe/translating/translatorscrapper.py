import logging
import traceback
from dataclasses import dataclass, field
from itertools import product
from typing import Iterable, Any

import requests
import requests.exceptions as request_exceptions

from .parsing.translationparser import TranslationParser, Record, WrongStatusCodeError, ConjugationParser, AbstractParser
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


def get_product(firsts, seconds, by_seconds=False):
    if by_seconds:
        return map(tuple, map(reversed, product(seconds, firsts)))
    return product(firsts, seconds)


class AbstractScrapper:

    def __init__(self, parser: AbstractParser, **kwargs):
        self._parser: AbstractParser = parser
        self._session: requests.sessions.Session | None = None

    def __setattr__(self, name, value):
        match name:
            case 'session':
                if isinstance(value, requests.sessions.Session):
                    self.__dict__['_' + name] = value
                else:
                    raise ValueError
            case _:
                super().__setattr__(name, value)


class TranslatorScrapper(AbstractScrapper):

    def __init__(self, **kwargs):
        super().__init__(parser=TranslationParser(), **kwargs)

    def translate(self, from_lang: str, to_langs: list[str, ...] | str, words: list[str, ...] | str, by_word=False) -> Iterable[TranslationResult]:
        if isinstance(words, str):
            words = [words]
        if isinstance(to_langs, str):
            words = [to_langs]
        langs_words = get_product(to_langs, words, by_word)
        for to_lang, word in langs_words:
            yield self.translate_single(from_lang, to_lang, word)

    def translate_single(self, from_lang: str, to_lang: str, word: str) -> TranslationResult:
        trans_args = TransArgs(from_lang, to_lang, word)
        try:
            records = self._translate_from_url(trans_args)
        except TranslatorArgumentException:
            logging.exception(f'Exception: Invalid argument {str(trans_args)}')
            records = [Record(ErrorMessages.INVALID_ARGUMENT.format(str(trans_args)))]
        return TranslationResult(trans_args, records)

    def _translate_from_url(self, trans_args: TransArgs) -> Iterable[Record]:
        try:
            page: requests.Response = self._session.get(trans_args.to_url(), allow_redirects=True)
            self._parser.set_page(page)
            yield from self._parser.parse()
        except WrongStatusCodeError as err:
            logging.error(f'{err.page.status_code}: {err.page.text}')
            yield Record(self._get_status_code_message(err, trans_args))
        except request_exceptions.ConnectionError as err:
            logging.exception(traceback.format_exc())
            yield Record(ErrorMessages.CONNECTION_ERROR)
        except TranslatorArgumentException:
            raise TranslatorArgumentException

    def _get_status_code_message(self, err: WrongStatusCodeError, trans_args: TransArgs) -> str:
        match err.page.status_code:
            case 404:
                return PageCodeMessages.PAGE_NOT_FOUND_404.format(str(trans_args))
            case 303:
                return PageCodeMessages.PAGE_NOT_FOUND_303
            case _:
                return PageCodeMessages.UNHANDLED_PAGE_FULL_MESSAGE.format(err.page.status_code)


class ConjugationScrapper(AbstractScrapper):

    def __init__(self, **kwargs):
        super().__init__(parser=ConjugationParser(), **kwargs)

    def get_conjugation(self, lang: str, word: str):
        trans_args = TransArgs(lang, 'en', word)
        page: requests.Response = self._session.get(f'{trans_args.to_url()}/fragment/details', allow_redirects=True)
        self._parser.set_page(page)
        return self._parser.parse()


class Scrapper:
    def __init__(self):
        self.args = TransArgs()
        self._connector = Connector()
        self._conjugation_scrapper = ConjugationScrapper()
        self._translation_scrapper = TranslatorScrapper()

    def scrap_translation(self, from_lang: str, to_langs: list[str, ...], words: list[str, ...], by_word=False) -> Iterable[TranslationResult]:
        self._connector.establish_session()
        self._translation_scrapper.session = self._connector.session

        yield from self._translation_scrapper.translate(from_lang, to_langs, words, by_word=by_word)

        self._connector.close_session()

    def scrap_conjugation(self, lang: str, word: str):
        self._connector.establish_session()
        self._conjugation_scrapper.session = self._connector.session

        yield from self._conjugation_scrapper.get_conjugation(lang, word)

        self._connector.close_session()

    def scrap_translation_and_conjugation(self, from_lang: str, to_lang: str, word: str, by_word=False) -> tuple[Iterable[TranslationResult], Any]:
        self._connector.establish_session()
        self._translation_scrapper.session = self._connector.session
        self._conjugation_scrapper.session = self._connector.session

        translation_result = self._translation_scrapper.translate(from_lang, to_lang, word, by_word=by_word)
        conjugation_result = self._conjugation_scrapper.get_conjugation(from_lang, word)
        yield translation_result, conjugation_result

        self._connector.close_session()
