from typing import Generator

from ..constants import TranslationParts


class Formatter:

    def format_translations(self, translations: Generator[list[dict, ...], ...]) -> Generator[list[dict, ...], ...]:
        return (self._format_translation(translation) for translation in translations)

    def _format_translation(self, translation: list[dict, ...]):
        for elem in translation:
            elem[TranslationParts.GENDER] = self._format_gender(elem[TranslationParts.GENDER])
            elem[TranslationParts.PART_OF_SPEECH] = self._format_part_of_speech(elem[TranslationParts.PART_OF_SPEECH])
        return translation

    def _format_gender(self, gender: str) -> str:
        if 'ż' in gender:
            gender = 'fem'
        elif 'ę' in gender:
            gender = 'masc'
        elif 'nijaki' in gender:
            gender = 'neut'
        return gender

    def _format_part_of_speech(self, part_of_speech: str) -> str:
        if 'rzecz' in part_of_speech:
            part_of_speech = 'noun'
        if 'czas' in part_of_speech:
            part_of_speech = 'verb'
        if 'przym' in part_of_speech:
            part_of_speech = 'adv.'
        return part_of_speech

    def format_translation_into_string(self, translation: list[dict, ...]):
        string = ""
        for i, elem in enumerate(translation):
            string += elem[TranslationParts.TRANSLATION]
            if i + 1 < len(translation):
                string += ', '
        return string

    def _format_translation_element_into_string(self, elem: dict[str, ...]):
        string = elem[TranslationParts.TRANSLATION]
        if elem[TranslationParts.GENDER]:
            string += f' [{elem[TranslationParts.GENDER]}]'
        if elem[TranslationParts.PART_OF_SPEECH]:
            string += f' ({elem[TranslationParts.PART_OF_SPEECH]})'
        return string
