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


@dataclass(frozen=True)
class Modes:
    MULTI_LANG: str = '-m'
    MULTI_WORD: str = '-w'
    SINGLE: str = '-s'
    LANG_LIMIT: str = '-l'
    SAVED_LANGS: str = '-ll'
    LAST: str = '-1'
    DEFAULT_TRANSLATIONAL_MODE: str = '-dm'
    SETTINGS: str = '-ss'
    HELP: str = '-h'
    ADD_LANG: str = '-al'
    REMOVE_LANG: str = '-rl'


@dataclass(frozen=True)
class FullModes:
    MULTI_LANG: str = '--multi'
    MULTI_WORD: str = '--word'
    SINGLE: str = '--single'
    LANG_LIMIT: str = '--limit'
    SAVED_LANGS: str = '--langs'
    LAST: str = '--last'
    DEFAULT_TRANSLATIONAL_MODE: str = '--default_mode'
    SETTINGS: str = '--settings'
    HELP: str = '--help'
    ADD_LANG: str = '--add_lang'
    REMOVE_LANG: str = '--remove_lang'


@dataclass(frozen=True)
class ModeTypes:
    TRANSLATIONAL: str = 'translational'
    CONFIGURATIONAL: str = 'configurational'
    DISPLAYABLE: str = 'displayable'


modes_map = {
    Modes.MULTI_LANG: FullModes.MULTI_LANG,
    Modes.MULTI_WORD: FullModes.MULTI_WORD,
    Modes.SINGLE: FullModes.SINGLE,
    Modes.LANG_LIMIT: FullModes.LANG_LIMIT,
    Modes.SAVED_LANGS: FullModes.SAVED_LANGS,
    Modes.LAST: FullModes.LAST,
    Modes.DEFAULT_TRANSLATIONAL_MODE: FullModes.DEFAULT_TRANSLATIONAL_MODE,
    Modes.SETTINGS: FullModes.SETTINGS,
    Modes.HELP: FullModes.HELP,
    Modes.ADD_LANG: FullModes.ADD_LANG,
    Modes.REMOVE_LANG: FullModes.REMOVE_LANG
}


modes_to_arity_map = {
    (FullModes.MULTI_LANG, FullModes.MULTI_WORD, FullModes.ADD_LANG, FullModes.REMOVE_LANG): -1,
    (FullModes.SINGLE, FullModes.SAVED_LANGS, FullModes.LANG_LIMIT, FullModes.LAST, FullModes.SETTINGS, FullModes.HELP, FullModes.DEFAULT_TRANSLATIONAL_MODE): 0,
    (FullModes.LANG_LIMIT, FullModes.LAST, FullModes.DEFAULT_TRANSLATIONAL_MODE): 1
}


mode_types_to_modes = {
    ModeTypes.TRANSLATIONAL: {FullModes.SINGLE, FullModes.MULTI_WORD, FullModes.MULTI_LANG},
    ModeTypes.CONFIGURATIONAL: {FullModes.LANG_LIMIT, FullModes.SAVED_LANGS, FullModes.LAST, FullModes.ADD_LANG, FullModes.REMOVE_LANG, FullModes.DEFAULT_TRANSLATIONAL_MODE},
    ModeTypes.DISPLAYABLE: {FullModes.LANG_LIMIT, FullModes.DEFAULT_TRANSLATIONAL_MODE, FullModes.SETTINGS, FullModes.HELP, FullModes.SAVED_LANGS},
}