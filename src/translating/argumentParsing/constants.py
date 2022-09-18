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
class SHORT_FLAGS:
    MULTI_LANG: str = '-m'
    MULTI_WORD: str = '-w'
    SINGLE: str = '-s'
    LANG_LIMIT: str = '-l'
    SAVED_LANGS: str = '-ll'
    LAST: str = '-1'
    DEFAULT_TRANSLATIONAL_MODE: str = '-dm'
    LAYOUT_ADJUSTMENT_MODE: str = '-la'
    ADJUSTMENT_LANG: str = '-lal'
    SETTINGS: str = '-ss'
    HELP: str = '-h'
    ADD_LANG: str = '-al'
    REMOVE_LANG: str = '-rl'


@dataclass(frozen=True)
class FLAGS:
    MULTI_LANG: str = '--multi'
    MULTI_WORD: str = '--word'
    SINGLE: str = '--single'
    LANG_LIMIT: str = '--limit'
    SAVED_LANGS: str = '--langs'
    LAST: str = '--last'
    DEFAULT_TRANSLATIONAL_MODE: str = '--default_mode'
    LAYOUT_ADJUSTMENT_MODE: str = '--layout_adjustment_mode'
    ADJUSTMENT_LANG: str = '--adjustment_lang'
    SETTINGS: str = '--settings'
    HELP: str = '--help'
    ADD_LANG: str = '--add_lang'
    REMOVE_LANG: str = '--remove_lang'


@dataclass(frozen=True)
class ModeTypes:
    TRANSLATIONAL: str = 'translational'
    CONFIGURATIONAL: str = 'configurational'
    DISPLAYABLE: str = 'displayable'


@dataclass(frozen=True)
class LanguageSpecificAdjustmentValues:
    NONE: str = 'none'
    NATIVE: str = 'native'
    KEYBOARD: str = 'keyboard'


short_to_usual_flags_dict = {
    SHORT_FLAGS.MULTI_LANG: FLAGS.MULTI_LANG,
    SHORT_FLAGS.MULTI_WORD: FLAGS.MULTI_WORD,
    SHORT_FLAGS.SINGLE: FLAGS.SINGLE,
    SHORT_FLAGS.LANG_LIMIT: FLAGS.LANG_LIMIT,
    SHORT_FLAGS.SAVED_LANGS: FLAGS.SAVED_LANGS,
    SHORT_FLAGS.LAST: FLAGS.LAST,
    SHORT_FLAGS.DEFAULT_TRANSLATIONAL_MODE: FLAGS.DEFAULT_TRANSLATIONAL_MODE,
    SHORT_FLAGS.LAYOUT_ADJUSTMENT_MODE: FLAGS.LAYOUT_ADJUSTMENT_MODE,
    SHORT_FLAGS.ADJUSTMENT_LANG: FLAGS.ADJUSTMENT_LANG,
    SHORT_FLAGS.SETTINGS: FLAGS.SETTINGS,
    SHORT_FLAGS.HELP: FLAGS.HELP,
    SHORT_FLAGS.ADD_LANG: FLAGS.ADD_LANG,
    SHORT_FLAGS.REMOVE_LANG: FLAGS.REMOVE_LANG,
}

flag_to_description_dict = {
    FLAGS.MULTI_LANG: '',
    FLAGS.MULTI_WORD: '',
    FLAGS.SINGLE: '',
    FLAGS.LANG_LIMIT: '',
    FLAGS.SAVED_LANGS: '',
    FLAGS.LAST: '',
    FLAGS.DEFAULT_TRANSLATIONAL_MODE: '',
    FLAGS.LAYOUT_ADJUSTMENT_MODE: "Replaces language-specific characters with corresponding characters of latin alphabet. 'keyboard' option replaces characters with those of the same placement at default English layout."\
                                  " 'native' option replaces characters to those of a corresponding pronunciation (or meaning in case of Chinese).",
    FLAGS.ADJUSTMENT_LANG: 'Language to work with the script adjustment',
    FLAGS.SETTINGS: '',
    FLAGS.HELP: '',
    FLAGS.ADD_LANG: '',
    FLAGS.REMOVE_LANG: '',
}


modes_to_arity_dict = {
    (FLAGS.MULTI_LANG, FLAGS.MULTI_WORD, FLAGS.ADD_LANG, FLAGS.REMOVE_LANG): -1,
    (FLAGS.SINGLE, FLAGS.SAVED_LANGS, FLAGS.LANG_LIMIT, FLAGS.LAST, FLAGS.SETTINGS, FLAGS.HELP, FLAGS.DEFAULT_TRANSLATIONAL_MODE): 0,
    (FLAGS.LANG_LIMIT, FLAGS.LAST, FLAGS.DEFAULT_TRANSLATIONAL_MODE, FLAGS.LAYOUT_ADJUSTMENT_MODE, FLAGS.ADJUSTMENT_LANG): 1
}


mode_types_to_modes = {
    ModeTypes.TRANSLATIONAL: {FLAGS.SINGLE, FLAGS.MULTI_WORD, FLAGS.MULTI_LANG},
    ModeTypes.CONFIGURATIONAL: {FLAGS.LANG_LIMIT, FLAGS.SAVED_LANGS, FLAGS.LAST, FLAGS.ADD_LANG, FLAGS.REMOVE_LANG, FLAGS.DEFAULT_TRANSLATIONAL_MODE, FLAGS.LAYOUT_ADJUSTMENT_MODE, FLAGS.ADJUSTMENT_LANG},
    ModeTypes.DISPLAYABLE: {FLAGS.LANG_LIMIT, FLAGS.DEFAULT_TRANSLATIONAL_MODE, FLAGS.SETTINGS, FLAGS.HELP, FLAGS.SAVED_LANGS, FLAGS.LAYOUT_ADJUSTMENT_MODE, FLAGS.ADJUSTMENT_LANG},
}

alphabet = 'abcdefghijklmnopqrstuvwxyz'