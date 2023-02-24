from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


class WrongStatusCodeError(ConnectionError):
    def __init__(self, page: requests.Response, *args):
        super().__init__(*args)
        self.page = page


@dataclass
class Record:
    translation: str = ''
    part_of_speech: str = ''
    gender: str = ''

    def __bool__(self):
        return any(filter(bool, (self.translation, self.part_of_speech, self.gender)))


class AbstractParser(ABC):

    def __init__(self, page: requests.Response = None, **kwargs):
        self._page = page

    def set_page(self, page: requests.Response):
        self._page = page

    def parse(self):
        if self._page.status_code != 200:
            raise WrongStatusCodeError(self._page)
        yield from self._parse()

    @abstractmethod
    def _parse(self):
        raise NotImplemented


class TranslationParser(AbstractParser):

    def __init__(self, page: requests.Response = None, **kwargs):
        super().__init__(page, **kwargs)

    def _parse(self) -> Iterable[Record]:
        soup = BeautifulSoup(self._page.text, features="html.parser")
        trans_elems = soup.find_all('div', {'class': 'py-1'})
        actual_trans = filter(lambda trans_elem: trans_elem.select_one('h3'), trans_elems)
        records = map(self._parse_single_translation_tag, actual_trans)
        return records

    def _parse_single_translation_tag(self, translation_tag: Tag) -> Record:
        translation = self._get_translation(translation_tag)
        spans = self._get_spans(translation_tag)
        part_of_speech = self._get_part_of_speech(spans)
        gender = self._get_gender(spans)
        return Record(translation, part_of_speech, gender)

    def _get_translation(self, translation_tag: Tag) -> str:
        return translation_tag.select_one('h3').text

    def _get_spans(self, translation_tag: Tag) -> list[Tag, ...]:
        main_span = translation_tag.select_one('span', {'class': 'text-xxs text-gray-500'})
        return main_span.findAll('span')

    def _get_part_of_speech(self, spans: list[Tag, ...]) -> str:
        return self._get_ith(spans, 0)

    def _get_gender(self, spans: list[Tag, ...]) -> str:
        return self._get_ith(spans, 1)

    def _get_ith(self, items: list[Tag, ...], i: int):
        return items[i].text if len(items) > i else ''


class ConjugationParser(AbstractParser):
    def __init__(self, page: requests.Response = None, **kwargs):
        super().__init__(**kwargs)
        self._page = page

    def _parse(self):
        return pd.read_html(self._page.text, keep_default_na=False, header=None)
