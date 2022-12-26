from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..constants import TranslationParts


class Parser:

    def __init__(self, page: requests.Response = None):
        self._page = page

    def set_page(self, page: requests.Response):
        self._page = page

    def parse(self) -> list[dict[str, str]]:
        if self._page.status_code == 200:
            return self._parse_translation()
        else:
            return [self._create_translation_part(self._page.status_code)]

    def _parse_translation(self):
        translations = []
        soup = BeautifulSoup(self._page.text, features="html.parser")
        for translation_element in soup.findAll('div', {'class': 'py-1'}):
            if translation_element.select_one('h3'):
                translations.append(self._parse_single_translation_tag(translation_element))
        return translations

    def _parse_single_translation_tag(self, translation_tag: Tag):
        translation = self._get_translation(translation_tag)
        span = self._get_spans(translation_tag)[0]
        description = span.replace('\n', ', ')[2:-2]
        # part_of_speech = self._get_part_of_speech(spans)
        # gender = self._get_gender(spans)
        return self._create_translation_part(translation, description)

    @staticmethod
    def _create_translation_part(translation: str | int, part_of_speech: str = '', gender: str = ''):
        return {
            TranslationParts.TRANSLATION: translation,
            TranslationParts.PART_OF_SPEECH: part_of_speech,
            TranslationParts.GENDER: gender
        }

    def _get_translation(self, translation_tag: Tag) -> str:
        return translation_tag.select_one('h3').text  # span[data-element="phrase"]

    def _get_spans(self, translation_tag: Tag) -> list[str, ...]:
        spans = translation_tag.findAll('span', {'class': 'text-xxs text-gray-500'})  # 'phrase__summary__field'
        return [s.text for s in spans]

    def _get_part_of_speech(self, spans: list[str, ...]) -> str:
        return self._get_ith_span(spans, 0)[1:-1]

    def _get_gender(self, spans: list[str, ...]) -> str:
        return self._get_ith_span(spans, 1)[1:-1]

    def _get_ith_span(self, spans: list[str, ...], i: int):
        return spans[i] if len(spans) > i else ""