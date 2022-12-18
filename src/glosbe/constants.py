from dataclasses import dataclass


@dataclass(frozen=True)
class SHORT_FLAGS:
    LAYOUT_ADJUSTMENT_MODE: str = '-la'
    ADJUSTMENT_LANG: str = '-lal'


@dataclass(frozen=True)
class FLAGS:
    LAYOUT_ADJUSTMENT_MODE: str = '--layout_adjustment_mode'
    ADJUSTMENT_LANG: str = '--adjustment_lang'


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