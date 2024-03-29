from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class WebConstants:
    MAIN_URL = "glosbe.com"


@dataclass
class TransArgs:
    from_lang: str = ''
    to_lang: str = ''
    word: str = ''

    def to_url(self) -> str:
        if not self:
            raise TranslatorArgumentException(self)
        return f'https://{WebConstants.MAIN_URL}/{self.from_lang}/{self.to_lang}/{self.word}'

    def __bool__(self):
        return all(filter(bool, (self.from_lang, self.to_lang, self.word)))


class TranslatorArgumentException(ValueError):
    def __init__(self, trans_args: TransArgs):
        self.trans_args = trans_args


class Connector:

    def __init__(self):
        self._session: requests.Session | None = None

    def establish_session(self):
        self._session = requests.Session()
        self._session.headers.update(Connector._get_default_headers())

    def __getattr__(self, name):
        match name:
            case 'session':
                return self._session
            case _:
                raise AttributeError

    def get_session(self) -> requests.Session:
        return self._session

    def close_session(self):
        self._session.close()

    def get_page(self, url: str) -> requests.Response:
        return self._session.get(url, allow_redirects=True)

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
