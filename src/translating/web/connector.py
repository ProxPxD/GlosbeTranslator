import logging
from dataclasses import dataclass

import requests

from . import utils
from .wrongStatusCodeException import WrongStatusCodeException
from ..constants import LogMessages, PageCodeMessages


@dataclass(frozen=True)
class WebConstants:
    MAIN_URL = "glosbe.com"


class Connector:

    def __init__(self, from_lang: str, to_lang: str = None, word: str = None):
        self._from_lang: str = from_lang
        self._to_lang: str = to_lang
        self._word: str = word

    def set_langs(self, from_lang, to_lang):
        self.set_from_lang(from_lang)
        self.set_to_lang(to_lang)

    def set_from_lang(self, from_lang: str):
        self._from_lang = from_lang

    def set_to_lang(self, to_lang: str):
        self._to_lang = to_lang

    def set_word(self, word: str):
        self._word = word

    def get_page(self):
        page: requests.Response = self._request_page()
        if page.status_code != 200:
            if page.status_code == 404:
                logging.warning(LogMessages.NO_TRANSLATION)
                return None
            logging.error(LogMessages.UNKNOWN_PAGE_STATUS.format(page.status_code))
            print(PageCodeMessages.PLEASE_REPORT)
            raise WrongStatusCodeException(page)
        return page

    def _request_page(self) -> requests.Response:
        url: str = self._create_target_url()
        return Connector._request_page_from_url(url)

    def _create_target_url(self):
        return utils.join_url_with_slashes(WebConstants.MAIN_URL, self._from_lang, self._to_lang, self._word)

    @staticmethod
    def _request_page_from_url(url: str):
        with requests.Session() as session:
            session.headers.update(Connector._get_default_headers())
            page = session.get(url, allow_redirects=False)
        return page

    @staticmethod
    def _get_default_headers() -> dict:
        return {'User-agent': 'Mozilla/5.0'}
        # {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        #     'Dnt': '1',
        #     'Host': 'httpbin.org',
        #     'Upgrade-Insecure-Requests': '1',
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
        #                   'AppleWebKit/537.36 (KHTML, like Gecko) '
        #                   'Chrome/83.0.4103.97 Safari/537.36',
        #     'X-Amzn-Trace-Id': 'Root=1-5ee7bbec-779382315873aa33227a5df6'
        # }
