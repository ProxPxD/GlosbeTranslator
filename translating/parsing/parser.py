from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class TranslationParts:
    TRANSLATION: str = 'translation'
    GENDER: str = 'gender'
    PART_OF_SPEECH: str = 'part of speech'


class Parser:

    def __init__(self, text=""):
        self._soup = None
        self._init_soup(text)

    def set_page_text(self, text: str):
        self._init_soup(text)

    def _init_soup(self, text: str):
        self._soup = BeautifulSoup(text, features="html.parser")

    def parse(self):
        translations = []
        for translation_element in self._soup.findAll('li', {'data-element': 'translation'}):
            translations.append(self._parse_single_translation_tag(translation_element))
        return translations

    def _parse_single_translation_tag(self, translation_tag: Tag):
        translation = self._get_translation(translation_tag)
        spans = self._get_spans(translation_tag)
        part_of_speech = self._get_part_of_speech(spans)
        gender = self._get_gender(spans)
        return {
            TranslationParts.TRANSLATION: translation,
            TranslationParts.PART_OF_SPEECH: part_of_speech,
            TranslationParts.GENDER: gender
        }

    def _get_translation(self, translation_tag: Tag) -> str:
        return translation_tag.select_one('span[data-element="phrase"]').text[1:-1]  # TODO check if and why the try except block is needed

    def _get_spans(self, translation_tag: Tag) -> list[str, ...]:
        spans = translation_tag.findAll('span', {'class': 'phrase__summary__field'})
        return [s.text for s in spans]

    def _get_part_of_speech(self, spans: list[str, ...]) -> str:
        return self._get_ith_span(spans, 0)

    def _get_gender(self, spans: list[str, ...]) -> str:
        return self._get_ith_span(spans, 1)

    def _get_ith_span(self, spans: list[str, ...], i: int):
        return spans[i] if len(spans) > i else ""