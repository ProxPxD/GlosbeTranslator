from dataclasses import dataclass

import requests

import utils


@dataclass(frozen=True)
class WebConstants:
    MAIN_URL = "glosbe.com"


class Connector:

    def __init__(self, from_lang: str, to_lang: str, word: str):
        self.from_lang: str = from_lang
        self.to_lang: str = to_lang
        self.word: str = word

    def get_page(self):
        page: requests.Response = self._request_page()
        if page.status_code != 200:
            raise ConnectionError(page)
        return page


    def _request_page(self) -> requests.Response:
        url: str = self._create_target_url()
        return Connector._request_page(url)

    def _create_target_url(self):
        return utils.join_url_with_slashes(WebConstants.MAIN_URL, self.from_lang, self.to_lang, self.word)

    @staticmethod
    def _request_page(url: str):
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