from dataclasses import dataclass


@dataclass(frozen=True)
class TranslationParts:
    TRANSLATION: str = 'translation'
    GENDER: str = 'gender'
    PART_OF_SPEECH: str = 'part of speech'


@dataclass(frozen=True)
class PageCodeMessages:
    UNHANDLED_PAGE_CODE: str = 'Unhandled page code'
    STATUS: str = 'Status'
    SAVING_IN_LOGS: str = 'Saving the necessary data in logs.'
    PLEASE_REPORT: str = 'Please, report the case'
