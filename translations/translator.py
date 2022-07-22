import requests

from web.connector import Connector
from parsing.parser import Parser


class Translator:

    def __init__(self, from_lang: str, to_lang: str, word: str):
        self._connector: Connector = Connector(from_lang, to_lang, word)
        self._parser: Parser = Parser()
        self._html: str = ""

    def connect(self):
        try:
            page: requests.Response = self._connector.get_page()
            self._parser.set_page_text(page.text)
        except ConnectionError as err:
            raise err

