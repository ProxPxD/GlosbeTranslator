import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..argumentParsing.constants import FLAGS, SHORT_FLAGS, LanguageSpecificAdjustmentValues


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent.parent.parent
    RESOURCES_DIR = WORKING_DIR / 'resources'


@dataclass(frozen=True)
class Configs:
    DEFAULT_TRANSLATIONAL_MODE: str = FLAGS.DEFAULT_TRANSLATIONAL_MODE
    LANG_LIMIT: str = FLAGS.LANG_LIMIT
    SAVED_LANGS: str = FLAGS.SAVED_LANGS
    LANG_SPEC_ADJUSTMENT: str = FLAGS.LAYOUT_ADJUSTMENT_MODE
    ADJUSTMENT_LANG: str = FLAGS.ADJUSTMENT_LANG
    DEFAULT_FILE_NAME: str = 'configurations'


lang_examples = '(np. en, pl, de, es)'
layout_examples = '(np. de, uk, ru, zh)'
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


class Configurations:

    _configs: dict = None
    _current_config_file: Path = ''

    @classmethod
    def init(cls, file_name=Configs.DEFAULT_FILE_NAME) -> None:
        if not Configurations._configs:
            if not Paths.RESOURCES_DIR.exists():
                Paths.RESOURCES_DIR.mkdir()
            cls._current_config_file = Paths.RESOURCES_DIR / file_name
            if not cls._current_config_file.exists():
                Configurations.init_default()
            Configurations._configs = Configurations._get_configurations()

    @classmethod
    def _get_configurations(cls) -> dict[str, Any]:
        with open(cls._current_config_file, 'r') as f:
            configs = json.load(f)
        return configs

    @classmethod
    def remove_current_configuration(cls):
        cls._current_config_file.unlink(missing_ok=True)

    @classmethod
    def save(cls) -> None:
        Configurations._save(Configurations._configs)

    @classmethod
    def save_and_close(cls) -> None:
        Configurations.save()
        Configurations._configs = None

    @classmethod
    def _save(cls, configs: dict) -> None:
        with open(cls._current_config_file, 'w') as f:
            json.dump(configs, f, indent=4, sort_keys=True)

    @classmethod
    def init_default(cls) -> None:
        Configurations._save(Configurations.__get_default_config())

    @classmethod
    def __get_default_config(cls) -> dict[str, Any]:
        return {
            Configs.DEFAULT_TRANSLATIONAL_MODE: '-s',
            Configs.LANG_LIMIT: 3,
            Configs.SAVED_LANGS: ['pl', 'en', 'de', 'es'],
            Configs.LANG_SPEC_ADJUSTMENT: 'none',
            Configs.ADJUSTMENT_LANG: '',
        }

    @classmethod
    def get_possible_values_for(cls, name: str):
        if name in _possible_config_values:
            return _possible_config_values[name]
        return None

    @classmethod
    def change_conf(cls, conf: str, value) -> None:
        if not Configurations._configs:
            Configurations.init()
        Configurations._configs[conf] = value

    @classmethod
    def set_conf(cls, conf: str, value) -> None:
        '''
        Alias for change_conf
        '''
        cls.change_conf(conf, value)

    @classmethod
    def get_conf(cls, name: str) -> Any:
        if name not in Configurations._configs:
            Configurations.add_default_config(name)
        return Configurations._configs[name]

    @classmethod
    def add_langs(cls, *arguments: str) -> None:
        langs = Configurations.get_saved_languages()
        for lang in arguments:
            if lang in langs:
                print()  # TODO: Messages.ADD_EXISTENT_LANG.format(lang))
            else:
                langs.append(lang)  # TODO replace with flags


    @classmethod
    def remove_langs(cls, *arguments: str):
        langs = Configurations.get_saved_languages()
        for lang in arguments:
            if lang not in langs:
                print()  # TODO: Messages.REMOVE_NONEXISTENT_LANG.format(lang))
            else:
                langs.remove(lang)

    @classmethod
    def add_default_config(cls, name: str):
        default = Configurations.__get_default_config()
        Configurations._configs[name] = default[name]
        Configurations.save()

    @classmethod
    def get_default_translation_mode(cls) -> str:
        return Configurations.get_conf(Configs.DEFAULT_TRANSLATIONAL_MODE)

    @classmethod
    def get_saved_languages(cls) -> list[str]:
        return Configurations.get_conf(Configs.SAVED_LANGS)

    @classmethod
    def get_from_language(cls) -> str:
        return Configurations.get_nth_saved_language(1)

    @classmethod
    def get_nth_saved_language(cls, index: int, to_skip: str = None) -> str:
        return Configurations.load_config_languages(to_skip)[index]

    @classmethod
    def load_config_languages(cls, *to_skips: str) -> list[str]:
        langs: list = Configurations.get_conf(Configs.SAVED_LANGS)[:]
        limit = int(Configurations.get_conf(Configs.LANG_LIMIT))
        for to_skip in to_skips:
            langs.remove(to_skip)
        if limit is not None and len(langs) > limit:
            langs = langs[:limit]
        return langs

    @classmethod
    def change_last_used_languages(cls, *langs: str) -> None:
        languages: list[str] = Configurations.get_conf(Configs.SAVED_LANGS)
        for lang in reversed(langs):
            if lang in languages:
                languages.remove(lang)
                languages.insert(0, lang)
        Configurations.change_conf(Configs.SAVED_LANGS, languages)
