import requests

from parsing.parser import Parser
from web.connector import Connector


class Translator:

    def __init__(self, from_lang: str, to_lang: str = None, word: str = None):
        self._connector: Connector = Connector(from_lang, to_lang, word)
        self._parser: Parser = Parser()
        self._html: str = ""

    def change_to_lang(self, to_lang: str):
        self._connector.set_to_lang(to_lang)

    def translate(self, word: str = None):
        try:
            if word:
                self._connector.set_word(word)
            page: requests.Response = self._connector.get_page()
            self._parser.set_page_text(page.text)
        except ConnectionError as err:
            raise err

