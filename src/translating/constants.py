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


@dataclass(frozen=True)
class LogMessages:
    NO_TRANSLATION: str = 'No translation has been found. Either the arguments were invalid or the requested translation does not exist so far'
    UNKNOWN_PAGE_STATUS: str = 'Unknown page status: {}'