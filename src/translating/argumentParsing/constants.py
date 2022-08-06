from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationErrors:
    MULTI_TRANSLATION_MODES_ON: str = 'Multi translation modes ({}) cannot be used at once!'


@dataclass(frozen=True)
class Messages:
    WRONG_MODE_TYPE: str = 'Wrong mode type: {}!'