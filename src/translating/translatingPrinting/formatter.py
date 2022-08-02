from __future__ import annotations

from typing import Any

from ..constants import TranslationParts, PageCodeMessages


class Formatter:

    def format_translations(self, translations):
        return (self._format_translation(translation) for translation in translations)

    def _format_translation(self, translation: list[dict, ...]):
        for elem in translation[1]:
            elem[TranslationParts.GENDER] = self._format_gender(elem[TranslationParts.GENDER])
            elem[TranslationParts.PART_OF_SPEECH] = self._format_part_of_speech(elem[TranslationParts.PART_OF_SPEECH])
        return translation

    def _format_gender(self, gender: str) -> str:
        if not gender:
            return gender

        if gender == 'feminine':
            gender = 'fem'
        elif gender == 'masculine':
            gender = 'masc'
        elif gender == 'neuter':
            gender = 'neut'
        return gender

    def _format_part_of_speech(self, part_of_speech: str) -> str:
        if part_of_speech == 'adverb':
            part_of_speech = 'adv.'
        if part_of_speech == 'adjective':
            part_of_speech = 'adj.'
        return part_of_speech

    def format_translation_into_string(self, translation: list[dict, Any]):
        string = ""
        for i, elem in enumerate(translation):
            string += self._format_translation_element_into_string(elem)
            if i + 1 < len(translation):
                string += ', '
        return string

    def _format_translation_element_into_string(self, elem: dict[str, Any]):
        string = self._format_raw_translation(elem[TranslationParts.TRANSLATION])
        if elem[TranslationParts.GENDER]:
            string += f' [{elem[TranslationParts.GENDER]}]'
        if elem[TranslationParts.PART_OF_SPEECH]:
            string += f' ({elem[TranslationParts.PART_OF_SPEECH]})'
        return string

    def _format_raw_translation(self, translation: str | int):
        if isinstance(translation, str):
            return translation
        return self._get_page_code_messages(translation)

    def _get_page_code_messages(self, code: int):
        if code == 404:
            return PageCodeMessages.PAGE_NOT_FOUND_404
        return PageCodeMessages.UNHANDLED_PAGE_FULL_MESSAGE.format(code)