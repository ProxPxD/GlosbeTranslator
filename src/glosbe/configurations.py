import json
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Iterable

from more_itertools import partition

from .translatingPrinting.translationPrinter import TranslationPrinter


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent.parent.parent
    RESOURCES_DIR = WORKING_DIR / 'resources'
    DEFAULT_CONF_FILE_NAME: str = 'configurations.json'


@dataclass(frozen=True)
class ConfigMessages:
    LANGUAGE_IN_SAVED: str = 'Language {} is already saved'
    LANGUAGE_NOT_IN_SAVED: str = 'Language {} has not been in saved'


class Configurations:

    _configs: dict = None
    _current_config_file: Path = ''

    @classmethod
    def init(cls, file_name=Paths.DEFAULT_CONF_FILE_NAME, default=None) -> None:
        config_file_to_init = Paths.RESOURCES_DIR / file_name
        if not cls._configs or cls._current_config_file != config_file_to_init:
            cls._current_config_file = config_file_to_init
            if not Paths.RESOURCES_DIR.exists():
                Paths.RESOURCES_DIR.mkdir()
            if not cls._current_config_file.exists():
                cls.init_file(default)
            cls._configs = cls._get_configurations()

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
    def init_file(cls, values=None) -> None:
        to_save = values if values else {}
        Configurations._save(to_save)

    @classmethod
    def change_conf(cls, conf: str, value) -> None:
        if Configurations._configs is None:
            Configurations.init()
        Configurations._configs[conf] = value

    @classmethod
    def set_conf(cls, conf: str, value) -> None:
        '''
        Alias for change_conf
        '''
        cls.change_conf(conf, value)

    @classmethod
    def get_all_configs(cls) -> dict[str, Any]:
        return dict(cls._configs)

    @classmethod
    def get_conf(cls, name: str) -> Any:  # TODO: think of default configs and setting them in case of new features
        return Configurations._configs[name]

    @classmethod
    def add_langs(cls, *arguments: str) -> None:
        langs = Configurations.get_saved_languages()
        not_saved, saved = partition(lambda lang: lang in langs, arguments)
        for lang in saved:
            TranslationPrinter.out(ConfigMessages.LANGUAGE_IN_SAVED.format(lang))
        for lang in not_saved:
            langs.append(lang)

    @classmethod
    def remove_langs(cls, *arguments: str):
        langs = Configurations.get_saved_languages()
        not_saved, saved = partition(lambda lang: lang in langs, arguments)
        for lang in saved:
            langs.remove(lang)
        for lang in not_saved:
            TranslationPrinter.out(ConfigMessages.LANGUAGE_NOT_IN_SAVED.format(lang))

    @classmethod
    def get_default_translation_mode(cls) -> str:
        return Configurations.get_conf('--default-mode')

    @classmethod
    def get_saved_languages(cls) -> list[str]:
        return Configurations.get_conf('--langs')

    @classmethod
    def get_from_language(cls) -> str:
        return Configurations.get_nth_saved_language(1)

    @classmethod
    def get_nth_saved_language(cls, index: int, *to_skips: str) -> str:
        langs = cls.load_config_languages(*to_skips)
        return next(islice(langs, int(index), None), None)

    @classmethod
    def load_config_languages_by_limit(cls, *to_skips: str, limit=None) -> Iterable[str]:
        if limit is None:
            limit = int(Configurations.get_conf('--limit'))
        langs = cls.load_config_languages(*to_skips)
        return islice(langs, limit)

    @classmethod
    def load_config_languages(cls, *to_skips: str) -> Iterable[str]:
        langs: list = Configurations.get_conf('--langs')[:]
        return filter(lambda lang: lang not in to_skips, langs)

    @classmethod
    def change_last_used_languages(cls, *langs: str) -> None:
        languages: list[str] = Configurations.get_saved_languages()
        for lang in reversed(langs):
            if lang in languages:
                languages.remove(lang)
                languages.insert(0, lang)
        Configurations.change_conf('--langs', languages)
