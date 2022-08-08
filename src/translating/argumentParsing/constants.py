from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationErrors:
    MULTI_TRANSLATION_MODES_ON: str = 'Multi translation modes ({}) cannot be used at once!'


@dataclass(frozen=True)
class Messages:
    WRONG_MODE_TYPE: str = 'Wrong mode type: {}!'
    HAS_NOT_BEEN_FOUND: str = ' has not been found!'
    ALREADY_EXISTS: str = ' already exists!'
    LANGUAGE_FORM: str = 'Language "{}"'
    ADD_EXISTENT_LANG: str = LANGUAGE_FORM + ALREADY_EXISTS
    REMOVE_NONEXISTENT_LANG: str = LANGUAGE_FORM + HAS_NOT_BEEN_FOUND
