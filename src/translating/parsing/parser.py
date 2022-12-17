from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..web.exceptions import WrongStatusCodeError


@dataclass
class Record:
    translation: str = ''
    part_of_speech: str = ''
    gender: str = ''


class Parser:

    def __init__(self, page: requests.Response = None):
        self._page = page

    def set_page(self, page: requests.Response):
        self._page = page

    def parse(self) -> list[Record]:
        if self._page.status_code != 200:
            raise WrongStatusCodeError(self._page)
        return self._parse_translation()

    def _parse_translation(self) -> list[Record]:
        translations = []
        soup = BeautifulSoup(self._page.text, features="html.parser")
        for translation_element in soup.findAll('li', {'data-element': 'translation'}):
            if translation_element.select_one('span[data-element="phrase"]'):
                translations.append(self._parse_single_translation_tag(translation_element))
        return translations

    def _parse_single_translation_tag(self, translation_tag: Tag) -> Record:
        translation = self._get_translation(translation_tag)
        spans = self._get_spans(translation_tag)
        part_of_speech = self._get_part_of_speech(spans)
        gender = self._get_gender(spans)
        return Record(translation, part_of_speech, gender)  # self._create_translation_part(translation, part_of_speech, gender)

    def _get_translation(self, translation_tag: Tag) -> str:
        return translation_tag.select_one('span[data-element="phrase"]').text[1:-1]

    def _get_spans(self, translation_tag: Tag) -> list[str, ...]:
        spans = translation_tag.findAll('span', {'class': 'phrase__summary__field'})
        return [s.text for s in spans]

    def _get_part_of_speech(self, spans: list[str, ...]) -> str:
        return self._get_ith_span(spans, 0)

    def _get_gender(self, spans: list[str, ...]) -> str:
        return self._get_ith_span(spans, 1)

    def _get_ith_span(self, spans: list[str, ...], i: int):
        return spans[i] if len(spans) > i else ""