import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import FLAGS, LanguageSpecificAdjustmentValues, SHORT_FLAGS


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent.parent.parent
    RESOURCES_DIR = WORKING_DIR / 'resources'
    CONFIG_FILE = RESOURCES_DIR / 'configurations.json'


@dataclass(frozen=True)
class Configs:
    DEFAULT_TRANSLATIONAL_MODE: str = FLAGS.DEFAULT_TRANSLATIONAL_MODE
    LANG_LIMIT: str = FLAGS.LANG_LIMIT
    SAVED_LANGS: str = FLAGS.SAVED_LANGS
    LANG_SPEC_ADJUSTMENT: str = FLAGS.LAYOUT_ADJUSTMENT_MODE
    ADJUSTMENT_LANG: str = FLAGS.ADJUSTMENT_LANG


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

    @staticmethod
    def init() -> None:
        if not Configurations._configs:
            if not Paths.RESOURCES_DIR.exists():
                Paths.RESOURCES_DIR.mkdir()
            if not Paths.CONFIG_FILE.exists():
                Configurations.init_default()
            Configurations._configs = Configurations._get_configurations()

    @staticmethod
    def _get_configurations() -> dict[str, Any]:
        with open(Paths.CONFIG_FILE, 'r') as f:
            configs = json.load(f)
        return configs

    @staticmethod
    def save() -> None:
        Configurations._save(Configurations._configs)

    @staticmethod
    def save_and_close() -> None:
        Configurations.save()
        Configurations._configs = None

    @staticmethod
    def _save(configs: dict) -> None:
        with open(Paths.CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=4, sort_keys=True)

    @staticmethod
    def init_default() -> None:
        Configurations._save(Configurations.__get_default_config())

    @staticmethod
    def __get_default_config() -> dict[str, Any]:
        return {
            Configs.DEFAULT_TRANSLATIONAL_MODE: '-s',
            Configs.LANG_LIMIT: 3,
            Configs.SAVED_LANGS: ['pl', 'en', 'de', 'es'],
            Configs.LANG_SPEC_ADJUSTMENT: 'none',
            Configs.ADJUSTMENT_LANG: '',
        }

    @staticmethod
    def get_possible_values_for(name: str):
        if name in _possible_config_values:
            return _possible_config_values[name]
        return None

    @staticmethod
    def change_conf(conf: str, value) -> None:
        if not Configurations._configs:
            Configurations.init()
        Configurations._configs[conf] = value

    @staticmethod
    def get_conf(name: str) -> Any:
        if name not in Configurations._configs:
            Configurations.add_default_config(name)
        return Configurations._configs[name]

    @staticmethod
    def add_default_config(name: str):
        default = Configurations.__get_default_config()
        Configurations._configs[name] = default[name]
        Configurations.save()

    @staticmethod
    def get_saved_languages() -> list[str]:
        return Configurations.get_conf(Configs.SAVED_LANGS)

    @staticmethod
    def get_nth_saved_language(index: int) -> str:
        return Configurations.get_saved_languages()[index]

    @staticmethod
    def load_config_languages(to_skip: str = None) -> list[str]:
        langs: list = Configurations.get_conf(Configs.SAVED_LANGS)[:]
        limit: int = int(Configurations.get_conf(Configs.LANG_LIMIT))
        if to_skip and to_skip in langs:
            langs.remove(to_skip)
        if limit is not None and len(langs) > limit:
            langs = langs[:limit]
        return langs

    @staticmethod
    def change_last_used_languages(*langs) -> None:
        languages: list[str] = Configurations.get_conf(Configs.SAVED_LANGS)
        for lang in reversed(langs):
            if lang in languages:
                languages.remove(lang)
                languages.insert(0, lang)
        Configurations.change_conf(Configs.SAVED_LANGS, languages)
