from dataclasses import dataclass


@dataclass(frozen=True)
class FLAGS:
    @dataclass(frozen=True)
    class MODES:
        SINGLE_LONG_FLAG = '--single'
        LANG_LONG_FLAG = '--lang'
        WORD_LONG_FLAG = '--word'
        SINGLE_SHORT_FLAG = '-s'
        LANG_SHORT_FLAG = '-m'
        WORD_SHORT_FLAG = '-w'

    @dataclass(frozen=True)
    class CONFIGURATIONAL:
        LANG_LIMIT_LONG_FLAG = '--limit'
        LANG_LIMIT_SHORT_FLAG = '-l'
        LANGS_SHOW_LONG_FLAG = '--langs'
        LANGS_SHOW_SHORT_FLAG = '-ll'
        LAST_LANG_LONG_FLAG = '--last'  # put number
        LAST_1_LONG_FLAG = '--last1'
        LAST_1_SHORT_FLAG = '-1'
        LAST_2_LONG_FLAG = '--last2'
        LAST_2_SHORT_FLAG = '-2'
        DEFAULT_MODE_LONG_FLAG = '--default-mode'
        DEFAULT_MODE_SHORT_FLAG = '-dm'
        SETTINGS_LONG_FLAG = '--settings'
        SETTINGS_SHORT_FLAG = '-ss'
        DOUBLE_MODE_STYLE_LONG_FLAG = '--double-mode-style'  # poss: lang word single/double
        DOUBLE_MODE_STYLE_SHORT_FLAG = '-ds'
        LAYOUT_ADJUSTMENT_METHOD_LONG_FLAG = '--layout-adjustment-method'
        LAYOUT_ADJUSTMENT_METHOD_SHORT_FLAG = '-lam'
        LAYOUT_ADJUSTMENT_LANG_LONG_FLAG = '--layout-adjustment-lang'
        LAYOUT_ADJUSTMENT_LANG_SHORT_FLAG = '-lal'
        ADD_LANG_LONG_FLAG = '--add-lang'
        ADD_LANG_SHORT_FLAG = '-al'
        REMOVE_LANG_LONG_FLAG = '--remove-lang'
        REMOVE_LANG_SHORT_FLAG = '-rl'

    @dataclass(frozen=True)
    class FUNCTIONAL:
        SILENT_LONG_FLAG = '--silent'
        REVERSE_LONG_FLAG = '--reverse'
        REVERSE_SHORT_FLAG = '-r'

    HELP_LONG_FLAG = '--help'
    HELP_SHORT_FLAG = '-h'


flag_to_description_dict = {
    FLAGS.LAYOUT_ADJUSTMENT_MODE: "Replaces language-specific characters with corresponding characters of latin alphabet. 'keyboard' option replaces characters with those of the same placement at default English layout."\
                                  " 'native' option replaces characters to those of a corresponding pronunciation (or meaning in case of Chinese).",
    FLAGS.ADJUSTMENT_LANG: 'Language to work with the script adjustment',
}

_possible_config_values = {
    Configs.DEFAULT_TRANSLATIONAL_MODE: [SHORT_FLAGS.SINGLE, SHORT_FLAGS.MULTI_LANG, SHORT_FLAGS.MULTI_WORD,
                                         FLAGS.SINGLE, FLAGS.MULTI_LANG, FLAGS.MULTI_WORD],
    Configs.LANG_SPEC_ADJUSTMENT: [LanguageSpecificAdjustmentValues.NONE,
                                   LanguageSpecificAdjustmentValues.NATIVE,
                                   LanguageSpecificAdjustmentValues.KEYBOARD],
    Configs.LANG_LIMIT: 'Any positive number or 0 to cancel the limit out',
    Configs.ADJUSTMENT_LANG: f'Any language of a different default layout than English or nothing {layout_examples}',
    Configs.SAVED_LANGS: f'Any language {lang_examples}',
}

lang_examples = '(np. en, pl, de, es)'
layout_examples = '(np. de, uk, ru, zh)'

def get_possible_values_for(name: str):
    if name in _possible_config_values:
        return _possible_config_values[name]
    return None