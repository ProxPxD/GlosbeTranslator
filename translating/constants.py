from dataclasses import dataclass


@dataclass
class TranslationParts:
    TRANSLATION: str = 'translation'
    GENDER: str = 'gender'
    PART_OF_SPEECH: str = 'part of speech'